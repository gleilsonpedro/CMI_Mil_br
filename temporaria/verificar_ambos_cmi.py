"""
Script para verificar ambos CMI e CMI-Mil de Abreulandia
"""
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
json_cmi = BASE_DIR / 'data' / 'output' / 'cmi_app3' / 'TO.json'
json_cmi_mil = BASE_DIR / 'data' / 'output' / 'cmi-mil_app3' / 'TO.json'

print("="*80)
print("VERIFICAÇÃO COMPLETA - ABREULANDIA")
print("="*80)

# 1. CMI
print("\n1. CMI (cmi_app3/TO.json) - Abreulandia:")
with open(json_cmi, 'r', encoding='utf-8') as f:
    dados_cmi = json.load(f)

abreu_cmi = [r for r in dados_cmi if 'ABREU' in r['Municipio'].upper()]
abreu_cmi_sorted = sorted(abreu_cmi, key=lambda x: x['Ano'])

print(f"   Total de registros: {len(abreu_cmi)}")
print("\n   Anos 2000-2010:")
for r in abreu_cmi_sorted:
    if 2000 <= r['Ano'] <= 2010:
        print(f"     {r['Ano']}: {r['Valor']}")

# 2. CMI-Mil
print("\n2. CMI-Mil (cmi-mil_app3/TO.json) - Abreulandia:")
with open(json_cmi_mil, 'r', encoding='utf-8') as f:
    dados_cmi_mil = json.load(f)

abreu_cmi_mil = [r for r in dados_cmi_mil if 'ABREU' in r['Municipio'].upper()]
abreu_cmi_mil_sorted = sorted(abreu_cmi_mil, key=lambda x: x['Ano'])

print(f"   Total de registros: {len(abreu_cmi_mil)}")
print("\n   Anos 2000-2010:")
for r in abreu_cmi_mil_sorted:
    if 2000 <= r['Ano'] <= 2010:
        print(f"     {r['Ano']}: {r['Valor']}")

# 3. Comparação lado a lado
print("\n3. COMPARAÇÃO LADO A LADO (2000-2010):")
print("   Ano    CMI      CMI-Mil")
print("   " + "-"*30)
for ano in range(2000, 2011):
    cmi_val = next((r['Valor'] for r in abreu_cmi_sorted if r['Ano'] == ano), 'N/A')
    cmi_mil_val = next((r['Valor'] for r in abreu_cmi_mil_sorted if r['Ano'] == ano), 'N/A')
    print(f"   {ano}   {cmi_val:6}   {cmi_mil_val:6}")

print("\n" + "="*80)
