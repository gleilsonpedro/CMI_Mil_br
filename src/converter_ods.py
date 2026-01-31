"""
Script para extrair dados das planilhas CMI-Mil.ods e CMI.ods
Processa dados de CMI (Coeficiente de Mortalidade Infantil) por UF
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
ARQUIVO_CMI_MIL = BASE_DIR / 'data' / 'input' / 'CMI-Mil.ods'
ARQUIVO_CMI = BASE_DIR / 'data' / 'input' / 'CMI.ods'
OUTPUT_DIR_CMI_MIL = BASE_DIR / 'data' / 'output' / 'CMI_MIL'
OUTPUT_DIR_CMI_PURO = BASE_DIR / 'data' / 'output' / 'CMI_puro'

# Lista de UFs do Brasil
UFS_BRASIL = [
    'AC', 'AL', 'AM', 'AP', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 
    'MG', 'MS', 'MT', 'PA', 'PB', 'PE', 'PI', 'PR', 'RJ', 'RN', 
    'RO', 'RR', 'RS', 'SC', 'SE', 'SP', 'TO'
]

def limpar_nome_coluna(col_name):
    """Remove espaços extras e padroniza nome de coluna"""
    if isinstance(col_name, str):
        return col_name.strip()
    return col_name

def identificar_tipo_aba(nome_aba, tipo_arquivo='CMI_MIL'):
    """
    Identifica se a aba é de uma UF específica
    Retorna: 'UF' ou None
    
    Para CMI_MIL: processa apenas abas "CMI-Mil UF"
    Para CMI_puro: processa abas "CMI UF"
    """
    nome_upper = nome_aba.upper().strip()
    
    # Pula abas de gráficos, informações gerais ou resumo
    abas_ignorar = ['GRÁFICO', 'GRAFICO', 'INFO', 'RESUMO', 'TOTAL', 'BR', 'BRASIL']
    if any(palavra in nome_upper for palavra in abas_ignorar):
        return None
    
    # IMPORTANTE: Para CMI-Mil.ods, ignorar abas de óbitos (OB) e nascidos vivos (NV)
    # Processar APENAS as abas "CMI-Mil UF"
    if tipo_arquivo == 'CMI_MIL':
        # Ignora abas OB e NV (óbitos e nascidos vivos)
        if ' OB' in nome_upper or ' NV' in nome_upper:
            return None
        
        # Processa apenas abas que começam com "CMI-MIL"
        if nome_upper.startswith('CMI-MIL ') or nome_upper.startswith('CMI-MIL'):
            # Formato: "CMI-Mil TO" ou "CMI-MIL TO"
            partes = nome_upper.split()
            if len(partes) >= 2:
                uf = partes[-1].strip()  # Pega última parte (a UF)
                if uf in UFS_BRASIL:
                    return uf
            elif len(partes) == 1 and nome_upper == 'CMI-MIL':
                # Aba resumo, ignorar
                return None
        return None
    
    # Para CMI.ods (CMI_puro): processa abas "CMI UF"
    if tipo_arquivo == 'CMI_puro':
        # Verifica se é "CMI UF" (para arquivo CMI.ods)
        if nome_upper.startswith('CMI '):
            partes = nome_upper.split()
            if len(partes) >= 2:
                uf = partes[1].strip()
                if uf in UFS_BRASIL:
                    return uf
        return None
    
    # Fallback para outros tipos
    # Verifica se o nome da aba é uma UF válida
    if nome_upper in UFS_BRASIL:
        return nome_upper
    
    # Verifica se começa com UF seguido de espaço ou hífen
    for uf in UFS_BRASIL:
        if nome_upper.startswith(uf + ' ') or nome_upper.startswith(uf + '-'):
            return uf
    
    return None

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
        if 'munic' in primeira_coluna:
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
    
    return 0  # Retorna 0 se não encontrar

def identificar_coluna_municipio(df):
    """
    Identifica qual coluna contém os nomes dos municípios
    """
    for col in df.columns:
        col_lower = str(col).lower()
        if 'munic' in col_lower:
            return col
    # Se não encontrar, assume que é a primeira coluna
    return df.columns[0]

def extrair_colunas_anos(df):
    """
    Extrai as colunas que representam anos (números de 1990 a 2030)
    """
    colunas_anos = []
    for col in df.columns:
        # Pula colunas óbvias que não são anos
        col_str = str(col).strip().upper()
        if 'MUNIC' in col_str or col_str in ['TOTAL', '#MUN', 'INIC', 'FIM']:
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

def limpar_nome_municipio(nome):
    """
    Remove códigos numéricos do início do nome do município
    e faz limpeza básica do texto
    """
    if not isinstance(nome, str):
        return nome
    
    # Remove espaços extras
    nome = nome.strip()
    
    # Remove números do início (ex: "120001 ACRELANDIA" -> "ACRELANDIA")
    # Usando regex para remover qualquer número seguido de espaço no início
    import re
    nome = re.sub(r'^\d+\s+', '', nome)
    
    # Normaliza espaços múltiplos
    nome = re.sub(r'\s+', ' ', nome)
    
    return nome.strip()

def processar_aba(df_ods, nome_aba, uf, tipo_cmi):
    """
    Processa uma aba específica e retorna DataFrame no formato longo
    """
    print(f"  Processando: {nome_aba} (UF: {uf}, Tipo: {tipo_cmi})")
    
    try:
        # Passo 1: Lê primeiras linhas para encontrar cabeçalho
        df_temp = df_ods.head(20)
        linha_cabecalho = encontrar_linha_cabecalho(df_temp)
        
        # Passo 2: Ajusta cabeçalho se necessário
        if linha_cabecalho > 0:
            df = df_ods.iloc[linha_cabecalho:].reset_index(drop=True)
            df.columns = df.iloc[0]
            df = df.drop(0).reset_index(drop=True)
        else:
            df = df_ods.copy()
        
        df.columns = [limpar_nome_coluna(col) for col in df.columns]
        
        # Passo 3: Identifica coluna de município
        coluna_municipio = identificar_coluna_municipio(df)
        if coluna_municipio not in df.columns:
            print(f"      Coluna de município não encontrada. Pulando aba.")
            return None
        
        df = df.rename(columns={coluna_municipio: 'Municipio'})
        
        # Passo 4: Identifica colunas de anos
        colunas_anos = extrair_colunas_anos(df)
        if not colunas_anos:
            print(f"      Nenhuma coluna de ano encontrada. Pulando aba.")
            return None
        
        # Passo 5: Seleciona apenas município e anos
        colunas_selecionar = ['Municipio'] + colunas_anos
        colunas_existentes = [col for col in colunas_selecionar if col in df.columns]
        df = df[colunas_existentes]
        
        # Passo 6: Remove linhas vazias logo no início
        df = df[df['Municipio'].notna()]
        df = df[df['Municipio'].astype(str).str.strip() != '']
        
        # Passo 7: Limpa nomes de municípios ANTES de converter para long
        df['Municipio'] = df['Municipio'].apply(limpar_nome_municipio)
        
        # Remove linhas que não são municípios (totais, notas, etc)
        textos_ignorar = [
            'TOTAL', 'IGNORADO', 'NOTAS:', 'NOTA:', 'FONTE:', 'DADOS FINAIS',
            'CONSULTE', 'INFORMAÇÕES', 'PRÉ-NATAL', 'VARIÁVEL', 'UTILIZADOS',
            'SISTEMA DE', 'SINASC', 'MS/SVSA', 'SECRETARIA', 'CONSOLIDA',
            'CATEGORIZA', 'ADEQUA', 'PARA MAIS', 'VEJA O DOCUMENTO',
            'DISPONÍVEIS ATÉ', 'PRELIMINARES', 'ATUALIZADOS'
        ]
        
        for texto in textos_ignorar:
            df = df[~df['Municipio'].str.upper().str.contains(texto, na=False, regex=False)]
        
        # Remove linhas que começam com aspas ou asteriscos
        df = df[~df['Municipio'].str.match(r'^[\"\*\-\.]', na=False)]
        
        # Remove linhas muito longas (provavelmente são notas de rodapé)
        df = df[df['Municipio'].str.len() < 100]
        
        # Remove linhas vazias novamente
        df = df[df['Municipio'].str.strip() != '']
        
        # Passo 8: Converte de formato largo para longo
        df_melted = df.melt(
            id_vars=['Municipio'], 
            var_name='Ano', 
            value_name='Valor'
        )
        
        # Passo 9: Limpeza dos dados
        df_melted['Valor'] = pd.to_numeric(df_melted['Valor'], errors='coerce').fillna(0).astype(float)
        df_melted['Ano'] = pd.to_numeric(df_melted['Ano'], errors='coerce').astype(int)
        df_melted['UF'] = uf
        df_melted['Tipo'] = tipo_cmi
        
        # Remove linhas com valores inválidos
        df_melted = df_melted[df_melted['Municipio'].notna()]
        df_melted = df_melted[df_melted['Ano'] >= 1990]
        
        print(f"    ✓ Processado: {len(df_melted)} registros | {len(df['Municipio'].unique())} municípios únicos")
        
        # Debug: mostra alguns nomes de municípios
        if len(df['Municipio'].unique()) > 0:
            exemplos = df['Municipio'].unique()[:5]
            print(f"      Exemplos: {', '.join(exemplos)}")
        
        return df_melted
        
    except Exception as e:
        print(f"      ❌ Erro ao processar aba: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def salvar_json(df, uf, tipo_cmi):
    """
    Salva DataFrame como JSON
    """
    if tipo_cmi == 'CMI_MIL':
        output_dir = OUTPUT_DIR_CMI_MIL
    else:
        output_dir = OUTPUT_DIR_CMI_PURO
    
    # Garante que o diretório existe
    output_dir.mkdir(parents=True, exist_ok=True)
    
    arquivo_saida = output_dir / f"{uf}.json"
    
    # Converte para dicionário e salva
    dados = df.to_dict(orient='records')
    
    with open(arquivo_saida, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    
    print(f"      💾 Salvo: {arquivo_saida.relative_to(BASE_DIR)}")

def limpar_jsons_antigos():
    """
    Remove todos os arquivos JSON existentes nas pastas de saída
    """
    print("\n" + "="*70)
    print(" LIMPANDO ARQUIVOS JSON ANTIGOS")
    print("="*70)
    
    diretorios = [OUTPUT_DIR_CMI_MIL, OUTPUT_DIR_CMI_PURO]
    total_removidos = 0
    
    for diretorio in diretorios:
        if diretorio.exists():
            arquivos_json = list(diretorio.glob('*.json'))
            for arquivo in arquivos_json:
                try:
                    arquivo.unlink()
                    total_removidos += 1
                    print(f"  🗑️  Removido: {arquivo.name}")
                except Exception as e:
                    print(f"  ⚠️  Erro ao remover {arquivo.name}: {e}")
    
    print(f"\n  Total de arquivos removidos: {total_removidos}")
    print("="*70)

def processar_planilha_ods(arquivo, tipo_cmi):
    """
    Processa uma planilha ODS específica
    """
    nome_arquivo = arquivo.name
    print(f"\n📊 Processando: {nome_arquivo}")
    
    # Verifica se arquivo existe
    if not arquivo.exists():
        print(f"  ❌ Arquivo não encontrado: {arquivo}")
        return {}
    
    try:
        # Lê arquivo ODS - obtém lista de abas primeiro
        xls = pd.read_excel(arquivo, sheet_name=None, engine='odf')
        nomes_abas = list(xls.keys())
        
        print(f"  📑 Total de abas encontradas: {len(nomes_abas)}\n")
        
        # Dicionários para agrupar dados por UF
        dados_por_uf = {}
        
        # Processa cada aba
        for i, nome_aba in enumerate(nomes_abas, 1):
            print(f"[{i}/{len(nomes_abas)}] Analisando: {nome_aba}")
            
            uf = identificar_tipo_aba(nome_aba, tipo_cmi)
            
            if uf is None:
                print(f"    ⏭️  Ignorando (não é aba de UF)")
                continue
            
            # Pega o DataFrame da aba
            df_aba = xls[nome_aba]
            
            df_processado = processar_aba(df_aba, nome_aba, uf, tipo_cmi)
            
            if df_processado is not None and len(df_processado) > 0:
                if uf not in dados_por_uf:
                    dados_por_uf[uf] = []
                dados_por_uf[uf].append(df_processado)
        
        return dados_por_uf
        
    except Exception as e:
        print(f"  ❌ Erro ao ler arquivo: {str(e)}")
        import traceback
        traceback.print_exc()
        return {}

def processar_todas_planilhas():
    """
    Função principal que processa todas as planilhas ODS
    """
    print("="*70)
    print(" 🚀 INICIANDO EXTRAÇÃO DE DADOS DAS PLANILHAS ODS")
    print("="*70)
    
    # Limpa JSONs antigos primeiro
    limpar_jsons_antigos()
    
    # Lista de arquivos para processar
    arquivos_processar = [
        (ARQUIVO_CMI_MIL, 'CMI_MIL'),
        (ARQUIVO_CMI, 'CMI_puro')
    ]
    
    print(f"\n📁 Diretório de entrada: {BASE_DIR / 'data' / 'input'}")
    print(f"📁 Saída CMI_MIL: {OUTPUT_DIR_CMI_MIL.relative_to(BASE_DIR)}")
    print(f"📁 Saída CMI_puro: {OUTPUT_DIR_CMI_PURO.relative_to(BASE_DIR)}")
    
    # Processa cada planilha
    todos_dados = {}
    for arquivo, tipo_cmi in arquivos_processar:
        dados = processar_planilha_ods(arquivo, tipo_cmi)
        for uf, dfs in dados.items():
            chave = (uf, tipo_cmi)
            if chave not in todos_dados:
                todos_dados[chave] = []
            todos_dados[chave].extend(dfs)
    
    # Salva JSONs agrupados por UF e tipo
    print("\n" + "="*70)
    print(" 💾 SALVANDO ARQUIVOS JSON")
    print("="*70 + "\n")
    
    total_registros = 0
    total_arquivos = 0
    
    for (uf, tipo_cmi), dfs in todos_dados.items():
        df_final = pd.concat(dfs, ignore_index=True)
        salvar_json(df_final, uf, tipo_cmi)
        total_registros += len(df_final)
        total_arquivos += 1
    
    print("\n" + "="*70)
    print(" ✅ EXTRAÇÃO CONCLUÍDA COM SUCESSO!")
    print("="*70)
    print(f"  📊 Total de arquivos gerados: {total_arquivos}")
    print(f"  📝 Total de registros processados: {total_registros:,}")
    print("="*70)
    
    # Análise de municípios
    analisar_municipios()

def analisar_municipios():
    """
    Analisa os nomes dos municípios nos JSONs gerados
    Verifica se há nomes incompletos
    """
    print("\n" + "="*70)
    print(" 🔍 ANÁLISE DE NOMES DE MUNICÍPIOS")
    print("="*70)
    
    todos_municipios = set()
    municipios_por_uf = {}
    
    # Lê todos os JSONs gerados
    for uf in UFS_BRASIL:
        arquivo_cmi_mil = OUTPUT_DIR_CMI_MIL / f"{uf}.json"
        arquivo_cmi_puro = OUTPUT_DIR_CMI_PURO / f"{uf}.json"
        
        municipios_uf = set()
        
        for arquivo in [arquivo_cmi_mil, arquivo_cmi_puro]:
            if arquivo.exists():
                with open(arquivo, 'r', encoding='utf-8') as f:
                    dados = json.load(f)
                    for item in dados:
                        municipio = item.get('Municipio', '')
                        if municipio:
                            municipios_uf.add(municipio)
                            todos_municipios.add(municipio)
        
        if municipios_uf:
            municipios_por_uf[uf] = municipios_uf
    
    print(f"\n  📊 Total de municípios únicos encontrados: {len(todos_municipios)}")
    print(f"  📊 Total de UFs com dados: {len(municipios_por_uf)}")
    
    # Testa busca de alguns municípios conhecidos
    print("\n  🔎 Testando busca de municípios:")
    municipios_teste = ['FORTALEZA', 'SAO PAULO', 'RIO DE JANEIRO', 'CRATEUS', 'BRASILIA']
    
    for municipio_teste in municipios_teste:
        encontrados = [m for m in todos_municipios if municipio_teste in m.upper()]
        if encontrados:
            print(f"    ✅ '{municipio_teste}': Encontrado(s) -> {', '.join(encontrados[:3])}")
        else:
            # Busca parcial
            parciais = [m for m in todos_municipios if m.upper().startswith(municipio_teste[:4])]
            if parciais:
                print(f"    ⚠️  '{municipio_teste}': Não encontrado exato, mas há similares -> {', '.join(parciais[:3])}")
            else:
                print(f"    ❌ '{municipio_teste}': Não encontrado")
    
    # Mostra exemplo de municípios de algumas UFs
    print("\n  📋 Exemplos de municípios por UF:")
    for uf in ['CE', 'SP', 'RJ'][:3]:
        if uf in municipios_por_uf:
            exemplos = sorted(list(municipios_por_uf[uf]))[:5]
            print(f"    {uf}: {', '.join(exemplos)}")
    
    print("="*70)

if __name__ == "__main__":
    processar_todas_planilhas()
