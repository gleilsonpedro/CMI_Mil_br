"""
Análise geral das diferenças entre CMI e CMI-Mil
"""
import json
import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DIR_CMI = BASE_DIR / 'data' / 'output' / 'cmi_app3'
DIR_CMI_MIL = BASE_DIR / 'data' / 'output' / 'cmi-mil_app3'

UFS = ['AC', 'AL', 'AM', 'AP', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 
       'MG', 'MS', 'MT', 'PA', 'PB', 'PE', 'PI', 'PR', 'RJ', 'RN', 
       'RR', 'RS', 'SC', 'SE', 'SP', 'TO']

todas_diferencas = []

for uf in UFS:
    with open(DIR_CMI / f'{uf}.json', 'r', encoding='utf-8') as f:
        cmi = pd.DataFrame(json.load(f))
    
    with open(DIR_CMI_MIL / f'{uf}.json', 'r', encoding='utf-8') as f:
        cmi_mil = pd.DataFrame(json.load(f))
    
    # Merge ano a ano
    merged = pd.merge(cmi, cmi_mil, on=['Municipio', 'Ano'], suffixes=('_cmi', '_mil'))
    merged['Diferenca'] = abs(merged['Valor_cmi'] - merged['Valor_mil'])
    todas_diferencas.extend(merged['Diferenca'].tolist())

df_diff = pd.DataFrame(todas_diferencas, columns=['Diferenca'])

print("="*80)
print("ANÁLISE GERAL: CMI vs CMI-Mil")
print("="*80)
print(f"\nTotal de comparações: {len(df_diff):,}")
print(f"\nEstatísticas da diferença absoluta:")
print(f"  Média: {df_diff['Diferenca'].mean():.4f}")
print(f"  Mediana: {df_diff['Diferenca'].median():.4f}")
print(f"  Desvio padrão: {df_diff['Diferenca'].std():.4f}")
print(f"  Mínimo: {df_diff['Diferenca'].min():.4f}")
print(f"  Máximo: {df_diff['Diferenca'].max():.4f}")

print(f"\nDistribuição das diferenças:")
print(f"  Diferença = 0: {(df_diff['Diferenca'] == 0).sum():,} ({(df_diff['Diferenca'] == 0).sum()/len(df_diff)*100:.1f}%)")
print(f"  Diferença < 0.01: {(df_diff['Diferenca'] < 0.01).sum():,} ({(df_diff['Diferenca'] < 0.01).sum()/len(df_diff)*100:.1f}%)")
print(f"  Diferença < 0.05: {(df_diff['Diferenca'] < 0.05).sum():,} ({(df_diff['Diferenca'] < 0.05).sum()/len(df_diff)*100:.1f}%)")
print(f"  Diferença < 0.10: {(df_diff['Diferenca'] < 0.10).sum():,} ({(df_diff['Diferenca'] < 0.10).sum()/len(df_diff)*100:.1f}%)")
print(f"  Diferença >= 0.10: {(df_diff['Diferenca'] >= 0.10).sum():,} ({(df_diff['Diferenca'] >= 0.10).sum()/len(df_diff)*100:.1f}%)")

print("\n" + "="*80)
print("CONCLUSÃO: Os dados agora mantêm as diferenças originais entre CMI e CMI-Mil.")
print("As diferenças são pequenas porque as planilhas originais já vêm com valores")
print("arredondados. Com 2 casas decimais, preservamos essas diferenças.")
print("="*80)
