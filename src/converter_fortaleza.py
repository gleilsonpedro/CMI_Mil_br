"""
Extrai os dados de Fortaleza por bairro da planilha CMI_Fortaleza.xlsx.
Gera JSONs separados para OB, NV, CMI e CMI_MIL em data/output/fortaleza.
"""
import json
import sys
from pathlib import Path

import pandas as pd


if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


BASE_DIR = Path(__file__).parent.parent
ARQUIVO_FORTALEZA = BASE_DIR / 'data' / 'input' / 'CMI_Fortaleza.xlsx'
OUTPUT_DIR = BASE_DIR / 'data' / 'output' / 'fortaleza'

ABAS_FORTALEZA = {
    'OB FORTALEZA': 'OB',
    'NV FORTALEZA': 'NV',
    'CMI-MIL FORTALEZA': 'CMI_MIL',
    'CMI-FORTALEZA': 'CMI',
}


def limpar_nome_coluna(col_name):
    if isinstance(col_name, str):
        return col_name.strip()
    return col_name


def encontrar_linha_cabecalho_bairros(df_temp):
    """Localiza a linha que contém o cabeçalho com a coluna de bairros."""
    for i, row in df_temp.iterrows():
        linha = [str(cell).strip() for cell in row.tolist()]
        primeira_coluna = linha[0].lower() if linha else ''

        if 'bair' in primeira_coluna:
            tem_anos = False
            for cell in linha[1:]:
                try:
                    valor = float(cell)
                    if 1990 <= valor <= 2030:
                        tem_anos = True
                        break
                except (TypeError, ValueError):
                    pass

            if tem_anos:
                return i

    return -1


def extrair_colunas_anos(df):
    """Extrai colunas numéricas que representam anos."""
    colunas_anos = []
    for col in df.columns:
        if isinstance(col, (int, float)):
            if 1990 <= float(col) <= 2030:
                colunas_anos.append(col)
            continue

        col_str = str(col).strip()
        if col_str.upper() in {'BAIRRO', 'BAIR.RES.MÃE', 'BAIR.RES.MAE', 'TOTAL'}:
            continue

        try:
            ano = float(col_str)
            if 1990 <= ano <= 2030:
                colunas_anos.append(col)
        except (TypeError, ValueError):
            pass

    return sorted(colunas_anos, key=lambda valor: float(valor))


def identificar_coluna_bairro(df):
    for col in df.columns:
        col_lower = str(col).lower()
        if 'bair' in col_lower:
            return col
    return None


def limpar_registros(df_melted):
    df_melted = df_melted[df_melted['Bairro'].notna()]
    df_melted['Bairro'] = df_melted['Bairro'].astype(str).str.strip()
    df_melted = df_melted[df_melted['Bairro'] != '']
    df_melted = df_melted[~df_melted['Bairro'].str.upper().isin(['TOTAL', 'IGNORADO'])]
    df_melted = df_melted[~df_melted['Bairro'].str.match(r'^[\"\*]', na=False)]

    textos_ignorar = [
        'CONSOLIDA', 'CATEGORIZA', 'ADEQUA', 'FONTE:', 'NOTA:',
        'CONSULTE', 'INFORMAÇÕES', 'PRÉ-NATAL', 'VARIÁVEL',
        'SISTEMA DE', 'SINASC', 'MS/SVSA', 'SECRETARIA', 'PERÍODO'
    ]
    for texto in textos_ignorar:
        df_melted = df_melted[~df_melted['Bairro'].str.upper().str.contains(texto, na=False)]

    return df_melted


def processar_aba(xls, nome_aba, tipo):
    print(f'  Processando: {nome_aba} ({tipo})')

    try:
        df_temp = pd.read_excel(xls, sheet_name=nome_aba, header=None, nrows=20)
        linha_cabecalho = encontrar_linha_cabecalho_bairros(df_temp)

        if linha_cabecalho == -1:
            print('    Cabeçalho não encontrado. Pulando.')
            return None

        df = pd.read_excel(xls, sheet_name=nome_aba, header=linha_cabecalho)
        df.columns = [limpar_nome_coluna(col) for col in df.columns]

        coluna_bairro = identificar_coluna_bairro(df)
        if not coluna_bairro:
            print('    Coluna de bairro não encontrada. Pulando.')
            return None

        colunas_anos = extrair_colunas_anos(df)
        if not colunas_anos:
            print('    Nenhuma coluna de ano encontrada. Pulando.')
            return None

        df = df[[coluna_bairro] + colunas_anos].rename(columns={coluna_bairro: 'Bairro'})
        df_melted = df.melt(id_vars=['Bairro'], var_name='Ano', value_name='Valor')
        df_melted['Ano'] = pd.to_numeric(df_melted['Ano'], errors='coerce').astype('Int64')
        df_melted['Valor'] = pd.to_numeric(df_melted['Valor'], errors='coerce').fillna(0)

        if tipo in {'OB', 'NV'}:
            df_melted['Valor'] = df_melted['Valor'].astype(int)

        df_melted = limpar_registros(df_melted)
        df_melted = df_melted[df_melted['Ano'].notna()]
        df_melted['Ano'] = df_melted['Ano'].astype(int)
        df_melted['Tipo'] = tipo

        print(f'    ✓ {len(df_melted)} registros')
        return df_melted
    except Exception as e:
        print(f'    Erro ao processar aba: {e}')
        return None


def salvar_json(df, tipo):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    arquivo_saida = OUTPUT_DIR / f'{tipo}.json'

    with open(arquivo_saida, 'w', encoding='utf-8') as f:
        json.dump(df.to_dict(orient='records'), f, ensure_ascii=False, indent=2)

    print(f'    Salvo: {arquivo_saida.relative_to(BASE_DIR)}')


def processar_fortaleza():
    print('=' * 70)
    print(' EXTRAINDO DADOS DE FORTALEZA')
    print('=' * 70)

    if not ARQUIVO_FORTALEZA.exists():
        print(f'Arquivo não encontrado: {ARQUIVO_FORTALEZA}')
        return

    xls = pd.ExcelFile(ARQUIVO_FORTALEZA)
    print(f'Abas encontradas: {len(xls.sheet_names)}')

    dados_por_tipo = {}

    for nome_aba in xls.sheet_names:
        tipo = ABAS_FORTALEZA.get(nome_aba.strip().upper())
        if not tipo:
            continue

        df_processado = processar_aba(xls, nome_aba, tipo)
        if df_processado is not None and not df_processado.empty:
            dados_por_tipo[tipo] = df_processado

    if not dados_por_tipo:
        print('Nenhum dado de Fortaleza foi processado.')
        return

    print('\nSalvando JSONs...')
    for tipo, df in dados_por_tipo.items():
        salvar_json(df, tipo)

    print('\nProcesso concluído com sucesso.')


if __name__ == '__main__':
    processar_fortaleza()