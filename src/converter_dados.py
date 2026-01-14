"""
Script para extrair dados da planilha DR_Rubens.xlsx
Processa abas de Nascidos Vivos (NV) e Óbitos (OB) por UF
Salva JSONs separados por UF em data/output/
"""
import pandas as pd
import json
import os
import sys
from pathlib import Path

# Garante encoding UTF-8 no terminal Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Configuração de caminhos
BASE_DIR = Path(__file__).parent.parent
ARQUIVO_EXCEL = BASE_DIR / 'data' / 'input' / 'CMI_Mil_Br_0_4.xlsx'
ARQUIVO_EXCEL_PURO = BASE_DIR / 'data' / 'input' / 'CMI_PURO_semMIL.xlsx'
OUTPUT_DIR_NV = BASE_DIR / 'data' / 'output' / 'nascidos_vivos'
OUTPUT_DIR_OB = BASE_DIR / 'data' / 'output' / 'obitos'
OUTPUT_DIR_CMI = BASE_DIR / 'data' / 'output' / 'CMI_MIL'
OUTPUT_DIR_CMI_PURO = BASE_DIR / 'data' / 'output' / 'CMI_puro'

def limpar_nome_coluna(col_name):
    """Remove espaços extras e padroniza nome de coluna"""
    if isinstance(col_name, str):
        return col_name.strip()
    return col_name

def identificar_tipo_aba(nome_aba, planilha_tipo='CMI_MIL'):
    """
    Identifica se a aba é de Nascidos Vivos (NV), Óbitos (OB), CMI_MIL ou CMI_puro
    Retorna: ('NV', 'UF'), ('OB', 'UF'), ('CMI_MIL', 'UF'), ('CMI_puro', 'UF') ou (None, None)
    """
    nome_upper = nome_aba.upper()
    
    # Pula abas de gráficos ou informações gerais
    abas_ignorar = ['GRÁFICO', 'GRAFICO', 'INFO', 'RESUMO', 'TOTAL']
    if any(palavra in nome_upper for palavra in abas_ignorar):
        return None, None
    
    # Para planilha CMI_PURO, procura abas que começam com "CMI"
    if planilha_tipo == 'CMI_puro':
        if nome_upper.startswith('CMI'):
            # Formato esperado: "CMI AC", "CMI_AC", "CMI-AC", "CMI SP", etc.
            if '_' in nome_aba:
                partes = nome_aba.split('_')
                if len(partes) >= 2:
                    uf = partes[1].strip().upper()
            elif ' ' in nome_aba:
                partes = nome_aba.split()
                if len(partes) >= 2:
                    uf = partes[1].strip().upper()
            elif '-' in nome_aba:
                partes = nome_aba.split('-')
                if len(partes) >= 2:
                    uf = partes[1].strip().upper()
            else:
                # Se não tiver separador, tenta pegar os últimos 2 caracteres
                uf = nome_aba[-2:].upper() if len(nome_aba) >= 2 else None
            
            # Valida se é um código de UF válido (2 letras)
            if uf and len(uf) == 2 and uf.isalpha():
                return 'CMI_puro', uf
        return None, None
    
    # Para planilha CMI_MIL (comportamento original)
    # Identifica abas CMI (exceto CMI_mil ou CMI-Mil que é resumo)
    if nome_upper.startswith('CMI'):
        if 'MIL' in nome_upper:
            return None, None
        # Formato esperado: "CMI_AC", "CMI AC", "CMI-AC", etc.
        if '_' in nome_aba:
            uf = nome_aba.split('_')[1].upper()
        elif ' ' in nome_aba:
            uf = nome_aba.split()[1].upper()
        elif '-' in nome_aba:
            uf = nome_aba.split('-')[1].upper()
        else:
            return None, None
        if uf:
            return 'CMI_MIL', uf
        return None, None
    
    # Identifica tipo (OB ou NV) e extrai UF
    if 'OB' in nome_upper:
        # Formato esperado: "AC OB" ou "AC-OB" ou "ACOB"
        uf = nome_aba.split()[0].upper() if ' ' in nome_aba else nome_aba[:2].upper()
        return 'OB', uf
    elif 'NV' in nome_upper:
        # Formato esperado: "AC NV" ou "AC-NV" ou "ACNV"
        uf = nome_aba.split()[0].upper() if ' ' in nome_aba else nome_aba[:2].upper()
        return 'NV', uf
    
    return None, None

def encontrar_linha_cabecalho(df_temp):
    """
    Procura a linha que contém o cabeçalho real (onde está 'Município' como coluna)
    Verifica se tem anos na mesma linha para confirmar que é o cabeçalho correto
    """
    for i, row in df_temp.iterrows():
        linha_texto = row.astype(str).tolist()
        linha_texto_lower = [str(cell).lower().strip() for cell in linha_texto]
        
        # Procura por município OU municipio na primeira coluna
        primeira_coluna = linha_texto_lower[0] if len(linha_texto_lower) > 0 else ""
        
        # Verifica se é exatamente "município" ou "municipio" (pode ter espaços)
        if primeira_coluna.strip() == "município" or primeira_coluna.strip() == "municipio":
            # Verifica se tem números (anos) nas outras colunas
            tem_anos = False
            for cell in linha_texto[1:]:
                try:
                    valor = float(cell)
                    # Aceita anos como float também (ex: 1996.0)
                    if 1990 <= valor <= 2030:
                        tem_anos = True
                        break
                except (ValueError, TypeError):
                    pass
            
            if tem_anos:
                return i
    
    return -1

def identificar_coluna_municipio(df):
    """
    Identifica qual coluna contém os nomes dos municípios
    """
    for col in df.columns:
        col_lower = str(col).lower()
        if 'munic' in col_lower:
            return col
    return None

def extrair_colunas_anos(df):
    """
    Extrai as colunas que representam anos (números de 1990 a 2030)
    """
    colunas_anos = []
    for col in df.columns:
        # Pula colunas óbvias que não são anos
        col_str = str(col).strip().upper()
        if col_str in ['MUNICIPIO', 'MUNICÍPIO', 'TOTAL', '#MUN', 'INIC', 'FIM']:
            continue
            
        # Se a coluna já é um número (int ou float)
        if isinstance(col, (int, float)):
            if 1990 <= col <= 2030:
                colunas_anos.append(col)
        else:
            # Tenta converter para número
            try:
                ano = float(col)
                if 1990 <= ano <= 2030:
                    colunas_anos.append(col)
            except (ValueError, TypeError):
                pass
    
    return sorted(colunas_anos)

def processar_aba(xls, nome_aba, tipo, uf):
    """
    Processa uma aba específica e retorna DataFrame no formato longo
    """
    print(f"  Processando: {nome_aba} (Tipo: {tipo}, UF: {uf})")
    
    try:
        # Passo 1: Lê primeiras linhas para encontrar cabeçalho
        df_temp = pd.read_excel(xls, sheet_name=nome_aba, header=None, nrows=20)
        linha_cabecalho = encontrar_linha_cabecalho(df_temp)
        
        if linha_cabecalho == -1:
            print(f"      Cabeçalho não encontrado. Pulando aba.")
            return None
        
        # Passo 2: Lê aba com cabeçalho correto
        df = pd.read_excel(xls, sheet_name=nome_aba, header=linha_cabecalho)
        df.columns = [limpar_nome_coluna(col) for col in df.columns]
        
        # Passo 3: Identifica coluna de município
        coluna_municipio = identificar_coluna_municipio(df)
        if not coluna_municipio:
            print(f"      Coluna de município não encontrada. Pulando aba.")
            return None
        
        df = df.rename(columns={coluna_municipio: 'Municipio'})
        
        # Passo 4: Identifica colunas de anos
        colunas_anos = extrair_colunas_anos(df)
        if not colunas_anos:
            print(f"      Nenhuma coluna de ano encontrada. Pulando aba.")
            return None
        
        # Passo 5: Seleciona apenas município e anos
        df = df[['Municipio'] + colunas_anos]
        
        # Passo 6: Converte de formato largo para longo
        df_melted = df.melt(
            id_vars=['Municipio'], 
            var_name='Ano', 
            value_name='Valor'
        )
        
        # Passo 7: Limpeza dos dados
        df_melted['Valor'] = pd.to_numeric(df_melted['Valor'], errors='coerce').fillna(0).astype(int)
        df_melted['Ano'] = pd.to_numeric(df_melted['Ano'], errors='coerce').astype(int)
        df_melted['UF'] = uf
        if tipo == 'CMI_MIL':
            df_melted['Tipo'] = 'CMI_MIL'
        elif tipo == 'CMI_puro':
            df_melted['Tipo'] = 'CMI_puro'
        else:
            df_melted['Tipo'] = 'Óbitos' if tipo == 'OB' else 'Nascidos Vivos'
        
        # Remove linhas vazias ou totais
        df_melted = df_melted[df_melted['Municipio'].notna()]
        df_melted = df_melted[~df_melted['Municipio'].str.upper().isin(['TOTAL', 'IGNORADO', ''])]
        df_melted['Municipio'] = df_melted['Municipio'].str.strip()
        
        # Remove notas de rodapé e textos explicativos
        # Primeiro remove linhas que começam com aspas ou asteriscos
        df_melted = df_melted[~df_melted['Municipio'].str.match(r'^[\"\*]', na=False)]
        
        # Depois remove linhas que contêm textos explicativos
        textos_ignorar = [
            'CONSOLIDA', 'CATEGORIZA', 'ADEQUA', 'FONTE:', 'NOTA:',
            'CONSULTE', 'INFORMAÇÕES', 'PRÉ-NATAL', 'VARIÁVEL',
            'SISTEMA DE', 'SINASC', 'MS/SVSA', 'SECRETARIA'
        ]
        for texto in textos_ignorar:
            df_melted = df_melted[~df_melted['Municipio'].str.upper().str.contains(texto, na=False)]
        
        print(f"    ✓ Processado: {len(df_melted)} registros")
        return df_melted
        
    except Exception as e:
        print(f"     Erro ao processar aba: {str(e)}")
        return None

def salvar_json(df, uf, tipo):
    """
    Salva DataFrame como JSON
    """
    if tipo == 'CMI_MIL':
        output_dir = OUTPUT_DIR_CMI
    elif tipo == 'CMI_puro':
        output_dir = OUTPUT_DIR_CMI_PURO
    elif tipo == 'OB':
        output_dir = OUTPUT_DIR_OB
    else:
        output_dir = OUTPUT_DIR_NV
    
    # Garante que o diretório existe
    output_dir.mkdir(parents=True, exist_ok=True)
    
    arquivo_saida = output_dir / f"{uf}.json"
    
    # Converte para dicionário e salva
    dados = df.to_dict(orient='records')
    
    with open(arquivo_saida, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    
    print(f"     Salvo: {arquivo_saida.relative_to(BASE_DIR)}")

def processar_planilha_individual(arquivo, planilha_tipo='CMI_MIL'):
    """
    Processa uma planilha específica
    """
    nome_arquivo = arquivo.name
    print(f"\n Processando: {nome_arquivo}")
    
    # Lê arquivo Excel
    xls = pd.ExcelFile(arquivo)
    print(f" Total de abas encontradas: {len(xls.sheet_names)}\n")
    
    # Dicionários para agrupar dados por UF e tipo
    dados_por_uf_tipo = {}
    
    # Processa cada aba
    for i, nome_aba in enumerate(xls.sheet_names, 1):
        print(f"[{i}/{len(xls.sheet_names)}] Analisando: {nome_aba}")
        
        tipo, uf = identificar_tipo_aba(nome_aba, planilha_tipo)
        
        if tipo is None:
            print(f"    Ignorando (não é aba de dados)")
            continue
        
        df_processado = processar_aba(xls, nome_aba, tipo, uf)
        
        if df_processado is not None and len(df_processado) > 0:
            chave = (uf, tipo)
            if chave not in dados_por_uf_tipo:
                dados_por_uf_tipo[chave] = []
            dados_por_uf_tipo[chave].append(df_processado)
    
    return dados_por_uf_tipo

def processar_planilha():
    """
    Função principal que processa todas as planilhas
    """
    print("="*70)
    print(" INICIANDO EXTRAÇÃO DE DADOS DAS PLANILHAS")
    print("="*70)
    
    # Verifica arquivos
    arquivos_processados = []
    
    if ARQUIVO_EXCEL.exists():
        arquivos_processados.append((ARQUIVO_EXCEL, 'CMI_MIL'))
    else:
        print(f"\n⚠ Arquivo não encontrado: {ARQUIVO_EXCEL.name}")
    
    if ARQUIVO_EXCEL_PURO.exists():
        arquivos_processados.append((ARQUIVO_EXCEL_PURO, 'CMI_puro'))
    else:
        print(f"\n⚠ Arquivo não encontrado: {ARQUIVO_EXCEL_PURO.name}")
    
    if not arquivos_processados:
        print(f"\n ERRO: Nenhum arquivo encontrado em: {ARQUIVO_EXCEL.parent}")
        return
    
    print(f"\n Saída NV: {OUTPUT_DIR_NV.relative_to(BASE_DIR)}")
    print(f" Saída OB: {OUTPUT_DIR_OB.relative_to(BASE_DIR)}")
    print(f" Saída CMI_MIL: {OUTPUT_DIR_CMI.relative_to(BASE_DIR)}")
    print(f" Saída CMI_puro: {OUTPUT_DIR_CMI_PURO.relative_to(BASE_DIR)}")
    
    # Processa cada planilha
    todos_dados = {}
    for arquivo, tipo_planilha in arquivos_processados:
        dados = processar_planilha_individual(arquivo, tipo_planilha)
        todos_dados.update(dados)
    
    # Salva JSONs agrupados por UF e tipo
    print("\n" + "="*70)
    print(" SALVANDO ARQUIVOS JSON")
    print("="*70 + "\n")
    
    total_registros = 0
    total_arquivos = 0
    
    for (uf, tipo), dfs in todos_dados.items():
        df_final = pd.concat(dfs, ignore_index=True)
        salvar_json(df_final, uf, tipo)
        total_registros += len(df_final)
        total_arquivos += 1
    
    print("\n" + "="*70)
    print(" EXTRAÇÃO CONCLUÍDA COM SUCESSO!")
    print("="*70)
    print(f" Total de arquivos gerados: {total_arquivos}")
    print(f" Total de registros processados: {total_registros:,}")
    print("="*70)

if __name__ == "__main__":
    processar_planilha()
