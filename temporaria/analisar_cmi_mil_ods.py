"""
Script para analisar a planilha CMI-Mil.ods - aba TO
"""
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
ARQUIVO_CMI_MIL = BASE_DIR / 'data' / 'input' / 'CMI-Mil.ods'

print("="*80)
print("ANÁLISE DA PLANILHA CMI-Mil.ods")
print("="*80)

# Listar abas relacionadas a TO
xls = pd.read_excel(ARQUIVO_CMI_MIL, sheet_name=None, engine='odf')
abas_to = [nome for nome in xls.keys() if 'TO' in nome.upper()]

print(f"\nAbas relacionadas a TO: {abas_to}")

# Verificar cada aba
for nome_aba in abas_to:
    print(f"\n{'='*80}")
    print(f"ABA: {nome_aba}")
    print('='*80)
    
    df = xls[nome_aba]
    print(f"Dimensões: {df.shape}")
    
    # Mostrar primeiras linhas
    print("\nPrimeiras 10 linhas:")
    for i in range(min(10, len(df))):
        row = df.iloc[i]
        print(f"  Linha {i}: {list(row[:6])}...")
    
    # Procurar Abreulandia
    for col in df.columns:
        col_values = df[col].astype(str).str.upper()
        if col_values.str.contains('ABREU', na=False).any():
            linha_idx = col_values[col_values.str.contains('ABREU', na=False)].index[0]
            print(f"\nAbreulandia encontrada na linha {linha_idx}, coluna {col}")
            print(f"Dados: {df.iloc[linha_idx][:10].tolist()}")
            break

print("\n" + "="*80)
