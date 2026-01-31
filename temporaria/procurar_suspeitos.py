"""
Procura municípios com diferença média próxima de zero entre CMI e CMI-Mil
"""
import json
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DIR_CMI = BASE_DIR / 'data' / 'output' / 'cmi_app3'
DIR_CMI_MIL = BASE_DIR / 'data' / 'output' / 'cmi-mil_app3'

UFS = ['AC', 'AL', 'AM', 'AP', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 
       'MG', 'MS', 'MT', 'PA', 'PB', 'PE', 'PI', 'PR', 'RJ', 'RN', 
       'RR', 'RS', 'SC', 'SE', 'SP', 'TO']

municipios_suspeitos = []

for uf in UFS:
    # Carrega dados
    with open(DIR_CMI / f'{uf}.json', 'r', encoding='utf-8') as f:
        cmi = pd.DataFrame(json.load(f))
    
    with open(DIR_CMI_MIL / f'{uf}.json', 'r', encoding='utf-8') as f:
        cmi_mil = pd.DataFrame(json.load(f))
    
    # Agrupa por município e calcula média
    cmi_media = cmi.groupby('Municipio')['Valor'].mean()
    cmi_mil_media = cmi_mil.groupby('Municipio')['Valor'].mean()
    
    # Calcula diferença média
    for municipio in cmi_media.index:
        if municipio in cmi_mil_media.index:
            diff = abs(cmi_media[municipio] - cmi_mil_media[municipio])
            if diff < 0.05:  # Diferença média menor que 0.05
                municipios_suspeitos.append({
                    'UF': uf,
                    'Municipio': municipio,
                    'CMI_media': round(cmi_media[municipio], 2),
                    'CMI_Mil_media': round(cmi_mil_media[municipio], 2),
                    'Diferenca': round(diff, 2)
                })

# Ordena por diferença
df_suspeitos = pd.DataFrame(municipios_suspeitos).sort_values('Diferenca')

print("="*80)
print(f"MUNICÍPIOS COM DIFERENÇA MÉDIA < 0.05 (Total: {len(df_suspeitos)})")
print("="*80)
print(df_suspeitos.head(20).to_string(index=False))
print("\n" + "="*80)
