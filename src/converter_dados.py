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
ARQUIVO_EXCEL = BASE_DIR / 'data' / 'input' / 'DR_Rubens.xlsx'
OUTPUT_DIR_NV = BASE_DIR / 'data' / 'output' / 'nascidos_vivos'
OUTPUT_DIR_OB = BASE_DIR / 'data' / 'output' / 'obitos'
OUTPUT_DIR_CMI = BASE_DIR / 'data' / 'output' / 'CMI'

def limpar_nome_coluna(col_name):
    """Remove espaços extras e padroniza nome de coluna"""
    if isinstance(col_name, str):
        return col_name.strip()
    return col_name

def identificar_tipo_aba(nome_aba):
    """
    Identifica se a aba é de Nascidos Vivos (NV), Óbitos (OB) ou CMI
    Retorna: ('NV', 'UF'), ('OB', 'UF'), ('CMI', 'UF') ou (None, None)
    """
    nome_upper = nome_aba.upper()
    
    # Pula abas de gráficos ou informações gerais
    abas_ignorar = ['GRÁFICO', 'GRAFICO', 'INFO', 'RESUMO', 'TOTAL']
    if any(palavra in nome_upper for palavra in abas_ignorar):
        return None, None
    
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
            return 'CMI', uf
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
        if tipo == 'CMI':
            df_melted['Tipo'] = 'CMI'
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
    if tipo == 'CMI':
        output_dir = OUTPUT_DIR_CMI
    elif tipo == 'OB':
        output_dir = OUTPUT_DIR_OB
    else:
        output_dir = OUTPUT_DIR_NV
    arquivo_saida = output_dir / f"{uf}.json"
    
    # Converte para dicionário e salva
    dados = df.to_dict(orient='records')
    
    with open(arquivo_saida, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    
    print(f"     Salvo: {arquivo_saida.relative_to(BASE_DIR)}")

def processar_planilha():
    """
    Função principal que processa toda a planilha
    """
    print("="*70)
    print(" INICIANDO EXTRAÇÃO DE DADOS DA PLANILHA")
    print("="*70)
    
    if not ARQUIVO_EXCEL.exists():
        print(f"\n ERRO: Arquivo não encontrado: {ARQUIVO_EXCEL}")
        print(f"   Por favor, coloque a planilha DR_Rubens.xlsx em: {ARQUIVO_EXCEL.parent}")
        return
    
    print(f"\n Arquivo: {ARQUIVO_EXCEL.name}")
    print(f" Saída NV: {OUTPUT_DIR_NV.relative_to(BASE_DIR)}")
    print(f" Saída OB: {OUTPUT_DIR_OB.relative_to(BASE_DIR)}")
    print(f" Saída CMI: {OUTPUT_DIR_CMI.relative_to(BASE_DIR)}")
    print()
    
    # Lê arquivo Excel
    xls = pd.ExcelFile(ARQUIVO_EXCEL)
    print(f" Total de abas encontradas: {len(xls.sheet_names)}\n")
    
    # Dicionários para agrupar dados por UF e tipo
    dados_por_uf_tipo = {}
    
    # Processa cada aba
    for i, nome_aba in enumerate(xls.sheet_names, 1):
        print(f"[{i}/{len(xls.sheet_names)}] Analisando: {nome_aba}")
        
        tipo, uf = identificar_tipo_aba(nome_aba)
        
        if tipo is None:
            print(f"    Ignorando (não é aba de dados)")
            continue
        
        df_processado = processar_aba(xls, nome_aba, tipo, uf)
        
        if df_processado is not None and len(df_processado) > 0:
            chave = (uf, tipo)
            if chave not in dados_por_uf_tipo:
                dados_por_uf_tipo[chave] = []
            dados_por_uf_tipo[chave].append(df_processado)
    
    # Salva JSONs agrupados por UF e tipo
    print("\n" + "="*70)
    print(" SALVANDO ARQUIVOS JSON")
    print("="*70 + "\n")
    
    total_registros = 0
    total_arquivos = 0
    
    for (uf, tipo), dfs in dados_por_uf_tipo.items():
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
