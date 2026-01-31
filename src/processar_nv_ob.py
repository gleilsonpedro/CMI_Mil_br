"""
Script para extrair dados de Nascidos Vivos e Óbitos da planilha CMI-Mil.ods
"""
import pandas as pd
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
ARQUIVO_CMI_MIL = BASE_DIR / 'data' / 'input' / 'CMI-Mil.ods'
OUTPUT_DIR_NV = BASE_DIR / 'data' / 'output' / 'nascidos_vivos'
OUTPUT_DIR_OB = BASE_DIR / 'data' / 'output' / 'obitos'

UFS_BRASIL = [
    'AC', 'AL', 'AM', 'AP', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 
    'MG', 'MS', 'MT', 'PA', 'PB', 'PE', 'PI', 'PR', 'RJ', 'RN', 
    'RO', 'RR', 'RS', 'SC', 'SE', 'SP', 'TO'
]

def limpar_nome_municipio(nome):
    """Remove código do início do nome do município"""
    import re
    if not isinstance(nome, str):
        return nome
    nome = nome.strip()
    nome = re.sub(r'^\d+\s+', '', nome)
    nome = re.sub(r'\s+', ' ', nome)
    return nome.strip()

def extrair_colunas_anos(df):
    """Extrai as colunas que representam anos (números de 1990 a 2030)"""
    colunas_anos = []
    for col in df.columns:
        col_str = str(col).strip().upper()
        
        # Ignorar colunas que não são anos
        if any(x in col_str for x in ['MUNIC', 'TOTAL', '#MUN', 'INIC', 'FIM', 'UNNAMED']):
            continue
            
        if isinstance(col, (int, float)):
            if 1990 <= col <= 2030:
                colunas_anos.append(col)
        else:
            try:
                ano = float(col)
                if 1990 <= ano <= 2030:
                    colunas_anos.append(col)
            except (ValueError, TypeError):
                pass
    
    return sorted(colunas_anos)

def processar_aba_nv_ob(df_aba, nome_aba, uf, tipo):
    """Processa uma aba de nascidos vivos ou óbitos"""
    print(f"  Processando: {nome_aba} (UF: {uf}, Tipo: {tipo})")
    
    try:
        # Encontrar cabeçalho
        linha_cabecalho = None
        for i, row in df_aba.iterrows():
            linha_texto = row.astype(str).tolist()
            if any('munic' in str(cell).lower() for cell in linha_texto):
                linha_cabecalho = i
                break
        
        if linha_cabecalho is None:
            print(f"    ⏭️  Cabeçalho não encontrado")
            return None
        
        # Ajustar DataFrame
        df = df_aba.iloc[linha_cabecalho:].reset_index(drop=True)
        df.columns = df.iloc[0]
        df = df.drop(0).reset_index(drop=True)
        
        # Identificar coluna de município
        col_municipio = df.columns[0]
        df = df.rename(columns={col_municipio: 'Municipio'})
        
        # Extrair colunas de anos
        colunas_anos = extrair_colunas_anos(df)
        if not colunas_anos:
            print(f"    ⏭️  Nenhuma coluna de ano encontrada")
            return None
        
        # Selecionar colunas
        colunas_existentes = ['Municipio'] + [col for col in colunas_anos if col in df.columns]
        df = df[colunas_existentes]
        
        # Limpar dados
        df = df[df['Municipio'].notna()]
        df = df[df['Municipio'].astype(str).str.strip() != '']
        df['Municipio'] = df['Municipio'].apply(limpar_nome_municipio)
        
        # Remover linhas que não são municípios
        textos_ignorar = ['TOTAL', 'IGNORADO', 'MUNICIPIO IGNORADO']
        for texto in textos_ignorar:
            df = df[~df['Municipio'].str.upper().str.contains(texto, na=False, regex=False)]
        
        # Converter para formato longo
        df_melted = df.melt(
            id_vars=['Municipio'], 
            var_name='Ano', 
            value_name='Valor'
        )
        
        # Limpeza dos dados
        df_melted['Valor'] = pd.to_numeric(df_melted['Valor'], errors='coerce').fillna(0).astype(int)
        df_melted['Ano'] = pd.to_numeric(df_melted['Ano'], errors='coerce').astype(int)
        df_melted['UF'] = uf
        df_melted['Tipo'] = tipo
        
        # Remover linhas inválidas
        df_melted = df_melted[df_melted['Municipio'].notna()]
        df_melted = df_melted[df_melted['Ano'] >= 1990]
        
        print(f"    ✓ Processado: {len(df_melted)} registros | {len(df['Municipio'].unique())} municípios")
        
        return df_melted
        
    except Exception as e:
        print(f"    ❌ Erro: {str(e)}")
        return None

def processar_nv_ob():
    """Processa todas as abas de nascidos vivos e óbitos"""
    print("="*80)
    print("PROCESSANDO NASCIDOS VIVOS E ÓBITOS")
    print("="*80)
    
    # Criar diretórios
    OUTPUT_DIR_NV.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR_OB.mkdir(parents=True, exist_ok=True)
    
    # Ler planilha
    xls = pd.read_excel(ARQUIVO_CMI_MIL, sheet_name=None, engine='odf')
    
    dados_nv = {}
    dados_ob = {}
    
    # Processar cada aba
    for nome_aba in xls.keys():
        nome_upper = nome_aba.upper().strip()
        
        # Identificar tipo e UF
        uf = None
        tipo = None
        
        if ' NV' in nome_upper:
            # Formato: "TO NV"
            partes = nome_upper.split()
            if len(partes) >= 2 and partes[0] in UFS_BRASIL:
                uf = partes[0]
                tipo = 'Nascidos_Vivos'
        
        elif ' OB' in nome_upper:
            # Formato: "TO OB"
            partes = nome_upper.split()
            if len(partes) >= 2 and partes[0] in UFS_BRASIL:
                uf = partes[0]
                tipo = 'Obitos'
        
        if uf and tipo:
            df_aba = xls[nome_aba]
            df_processado = processar_aba_nv_ob(df_aba, nome_aba, uf, tipo)
            
            if df_processado is not None:
                if tipo == 'Nascidos_Vivos':
                    dados_nv[uf] = df_processado
                else:
                    dados_ob[uf] = df_processado
    
    # Salvar JSONs
    print("\n" + "="*80)
    print("SALVANDO ARQUIVOS JSON")
    print("="*80)
    
    for uf, df in dados_nv.items():
        arquivo = OUTPUT_DIR_NV / f"{uf}.json"
        dados = df.to_dict(orient='records')
        with open(arquivo, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        print(f"  ✓ Nascidos Vivos: {uf}.json ({len(dados)} registros)")
    
    for uf, df in dados_ob.items():
        arquivo = OUTPUT_DIR_OB / f"{uf}.json"
        dados = df.to_dict(orient='records')
        with open(arquivo, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        print(f"  ✓ Óbitos: {uf}.json ({len(dados)} registros)")
    
    print("\n" + "="*80)
    print("✅ PROCESSAMENTO CONCLUÍDO")
    print("="*80)
    print(f"  Nascidos Vivos: {len(dados_nv)} estados")
    print(f"  Óbitos: {len(dados_ob)} estados")
    print("="*80)

if __name__ == "__main__":
    processar_nv_ob()
