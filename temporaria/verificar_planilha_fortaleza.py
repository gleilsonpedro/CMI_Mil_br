import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
ARQUIVO_CMI = BASE_DIR / 'data' / 'input' / 'CMI.ods'
ARQUIVO_CMI_MIL = BASE_DIR / 'data' / 'input' / 'CMI-Mil.ods'

print("="*80)
print("VERIFICANDO FORTALEZA NAS PLANILHAS ORIGINAIS")
print("="*80)

# Verificar CMI.ods
print("\n📄 CMI.ods - Aba CE:")
try:
    df_cmi = pd.read_excel(ARQUIVO_CMI, sheet_name='CMI CE', engine='odf')
    print(f"Total de linhas: {len(df_cmi)}")
    print(f"Colunas: {df_cmi.columns.tolist()[:10]}")
    
    # Procurar Fortaleza
    for i, row in df_cmi.iterrows():
        if 'FORTALEZA' in str(row.iloc[0]).upper():
            print(f"\nLinha {i}: {row.iloc[0]}")
            print(f"Primeiros 10 valores: {row.iloc[1:11].tolist()}")
            break
except Exception as e:
    print(f"Erro: {e}")

# Verificar CMI-Mil.ods
print("\n📄 CMI-Mil.ods - Aba CMI-Mil CE:")
try:
    df_cmi_mil = pd.read_excel(ARQUIVO_CMI_MIL, sheet_name='CMI-Mil CE', engine='odf')
    print(f"Total de linhas: {len(df_cmi_mil)}")
    print(f"Colunas: {df_cmi_mil.columns.tolist()[:10]}")
    
    # Procurar Fortaleza
    for i, row in df_cmi_mil.iterrows():
        if 'FORTALEZA' in str(row.iloc[0]).upper():
            print(f"\nLinha {i}: {row.iloc[0]}")
            print(f"Primeiros 10 valores: {row.iloc[1:11].tolist()}")
            break
except Exception as e:
    print(f"Erro: {e}")

print("\n" + "="*80)
