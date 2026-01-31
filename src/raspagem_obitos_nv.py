"""
Script para extrair dados de Nascidos Vivos (NV) e Óbitos (OB) da planilha CMI-Mil.ods
Padrão das abas: SIGLA_UF + NV ou SIGLA_UF + OB (ex: TO NV, TO OB, SP NV, SP OB)
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

def extrair_codigo_municipio(nome_original):
    """Extrai o código do município (6 dígitos no início)"""
    import re
    if not isinstance(nome_original, str):
        return None
    match = re.match(r'^(\d{6})', nome_original.strip())
    return match.group(1) if match else None

def processar_aba(df_aba, nome_aba, uf, tipo):
    """Processa uma aba de nascidos vivos ou óbitos"""
    print(f"  📋 {nome_aba} ({tipo})")
    
    try:
        # Encontrar linha do cabeçalho (linha que contém 'Município')
        linha_cabecalho = None
        for i, row in df_aba.iterrows():
            linha_texto = row.astype(str).tolist()
            if any('munic' in str(cell).lower() for cell in linha_texto):
                linha_cabecalho = i
                break
        
        if linha_cabecalho is None:
            print(f"    ⏭️  Cabeçalho não encontrado")
            return None
        
        # Ajustar DataFrame para começar do cabeçalho
        df = df_aba.iloc[linha_cabecalho:].reset_index(drop=True)
        df.columns = df.iloc[0]
        df = df.drop(0).reset_index(drop=True)
        
        # Primeira coluna é sempre município
        col_municipio = df.columns[0]
        
        # Extrair anos (colunas numéricas entre 1990-2030, ignorando strings e valores inválidos)
        colunas_anos = []
        for col in df.columns[1:]:  # Pular primeira coluna (município)
            # Se a coluna é string, ignorar (ex: '#Mun', 'Inic', 'Fim')
            if isinstance(col, str):
                continue
            
            # Se é número, verificar se é ano válido
            if isinstance(col, (int, float)):
                try:
                    ano = int(col)
                    if 1990 <= ano <= 2030:
                        colunas_anos.append(col)
                except (ValueError, TypeError):
                    pass
        
        if not colunas_anos:
            print(f"    ⏭️  Nenhuma coluna de ano válida")
            return None
        
        # Selecionar apenas município + anos
        df = df[[col_municipio] + colunas_anos].copy()
        df = df.rename(columns={col_municipio: 'Municipio_Original'})
        
        # Limpar dados
        df = df[df['Municipio_Original'].notna()]
        df = df[df['Municipio_Original'].astype(str).str.strip() != '']
        
        # Extrair código e limpar nome
        df['Codigo_Municipio'] = df['Municipio_Original'].apply(extrair_codigo_municipio)
        df['Municipio'] = df['Municipio_Original'].apply(limpar_nome_municipio)
        
        # Remover linhas que não são municípios válidos
        textos_ignorar = ['TOTAL', 'IGNORADO', 'MUNICIPIO IGNORADO']
        for texto in textos_ignorar:
            df = df[~df['Municipio'].str.upper().str.contains(texto, na=False, regex=False)]
        
        # Remover linhas sem código de município
        df = df[df['Codigo_Municipio'].notna()]
        
        # Converter para formato longo
        df_melted = df.melt(
            id_vars=['Municipio', 'Codigo_Municipio'], 
            value_vars=colunas_anos,
            var_name='Ano', 
            value_name='Valor'
        )
        
        # Limpeza e conversão
        df_melted['Valor'] = pd.to_numeric(df_melted['Valor'], errors='coerce').fillna(0).astype(int)
        df_melted['Ano'] = pd.to_numeric(df_melted['Ano'], errors='coerce').astype(int)
        df_melted['UF'] = uf
        df_melted['Tipo'] = tipo
        
        # Remover linhas inválidas
        df_melted = df_melted[df_melted['Ano'] >= 1990]
        
        print(f"    ✅ {len(df_melted)} registros | {len(df['Municipio'].unique())} municípios | {len(colunas_anos)} anos")
        
        return df_melted
        
    except Exception as e:
        print(f"    ❌ Erro: {str(e)}")
        return None

def processar_todas_abas():
    """Processa todas as abas de NV e OB"""
    print("="*80)
    print("🔍 RASPAGEM DE NASCIDOS VIVOS E ÓBITOS")
    print("="*80)
    
    # Criar diretórios
    OUTPUT_DIR_NV.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR_OB.mkdir(parents=True, exist_ok=True)
    
    # Ler todas as abas da planilha
    print("\n📂 Carregando planilha CMI-Mil.ods...")
    xls = pd.read_excel(ARQUIVO_CMI_MIL, sheet_name=None, engine='odf')
    print(f"   ✓ {len(xls)} abas encontradas")
    
    dados_nv = {}
    dados_ob = {}
    
    print("\n" + "="*80)
    print("📊 PROCESSANDO ABAS")
    print("="*80)
    
    # Processar cada aba
    for nome_aba in sorted(xls.keys()):
        nome_upper = nome_aba.upper().strip()
        
        # Identificar UF e tipo pela estrutura: "UF NV" ou "UF OB"
        partes = nome_upper.split()
        
        if len(partes) >= 2:
            uf_candidata = partes[0]
            tipo_aba = partes[1]
            
            # Verificar se é uma UF válida
            if uf_candidata in UFS_BRASIL:
                if tipo_aba == 'NV':
                    # Nascidos Vivos
                    df_processado = processar_aba(xls[nome_aba], nome_aba, uf_candidata, 'Nascidos_Vivos')
                    if df_processado is not None:
                        dados_nv[uf_candidata] = df_processado
                
                elif tipo_aba == 'OB':
                    # Óbitos
                    df_processado = processar_aba(xls[nome_aba], nome_aba, uf_candidata, 'Obitos')
                    if df_processado is not None:
                        dados_ob[uf_candidata] = df_processado
    
    # Salvar JSONs
    print("\n" + "="*80)
    print("💾 SALVANDO ARQUIVOS JSON")
    print("="*80)
    
    total_registros_nv = 0
    total_registros_ob = 0
    
    print("\n📈 Nascidos Vivos:")
    for uf in sorted(dados_nv.keys()):
        df = dados_nv[uf]
        arquivo = OUTPUT_DIR_NV / f"{uf}.json"
        dados = df.to_dict(orient='records')
        with open(arquivo, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        total_registros_nv += len(dados)
        print(f"  ✓ {uf}.json - {len(dados):,} registros")
    
    print("\n💀 Óbitos:")
    for uf in sorted(dados_ob.keys()):
        df = dados_ob[uf]
        arquivo = OUTPUT_DIR_OB / f"{uf}.json"
        dados = df.to_dict(orient='records')
        with open(arquivo, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        total_registros_ob += len(dados)
        print(f"  ✓ {uf}.json - {len(dados):,} registros")
    
    print("\n" + "="*80)
    print("✅ RASPAGEM CONCLUÍDA COM SUCESSO")
    print("="*80)
    print(f"  📈 Nascidos Vivos: {len(dados_nv)} estados | {total_registros_nv:,} registros")
    print(f"  💀 Óbitos: {len(dados_ob)} estados | {total_registros_ob:,} registros")
    print(f"  📁 Salvos em: {OUTPUT_DIR_NV.parent}")
    print("="*80)

if __name__ == "__main__":
    processar_todas_abas()
