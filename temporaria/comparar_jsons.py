"""
Script para identificar de onde vem os arquivos cmi_app3
"""
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

# Comparar estrutura dos JSONs
json_cmi_puro = BASE_DIR / 'data' / 'output' / 'CMI_puro' / 'TO.json'
json_cmi_app3 = BASE_DIR / 'data' / 'output' / 'cmi_app3' / 'TO.json'

print("="*80)
print("COMPARAÇÃO DOS JSONS")
print("="*80)

# 1. CMI_puro
print("\n1. CMI_puro/TO.json - Abreulandia:")
with open(json_cmi_puro, 'r', encoding='utf-8') as f:
    dados_puro = json.load(f)

abreu_puro = [r for r in dados_puro if 'ABREU' in r['Municipio'].upper()]
abreu_puro_sorted = sorted(abreu_puro, key=lambda x: x['Ano'])

print(f"   Total de registros: {len(abreu_puro)}")
print(f"   Estrutura: {list(abreu_puro[0].keys()) if abreu_puro else 'N/A'}")
print("\n   Anos e valores:")
for r in abreu_puro_sorted[:15]:
    print(f"     {r['Ano']}: {r['Valor']}")

# 2. cmi_app3
print("\n2. cmi_app3/TO.json - Abreulandia:")
with open(json_cmi_app3, 'r', encoding='utf-8') as f:
    dados_app3 = json.load(f)

abreu_app3 = [r for r in dados_app3 if 'ABREU' in r['Municipio'].upper()]
abreu_app3_sorted = sorted(abreu_app3, key=lambda x: x['Ano'])

print(f"   Total de registros: {len(abreu_app3)}")
print(f"   Estrutura: {list(abreu_app3[0].keys()) if abreu_app3 else 'N/A'}")
print("\n   Anos e valores:")
for r in abreu_app3_sorted[:15]:
    print(f"     {r['Ano']}: {r['Valor']}")

# 3. Verificar diferenças
print("\n3. DIFERENÇAS:")
print(f"   CMI_puro tem {len(abreu_puro)} registros")
print(f"   cmi_app3 tem {len(abreu_app3)} registros")
print(f"   Diferença: {len(abreu_puro) - len(abreu_app3)} registros")

# Verificar se cmi_app3 filtra zeros
zeros_puro = [r for r in abreu_puro if r['Valor'] == 0.0]
zeros_app3 = [r for r in abreu_app3 if r['Valor'] == 0.0]
print(f"\n   Registros com valor 0 em CMI_puro: {len(zeros_puro)}")
print(f"   Registros com valor 0 em cmi_app3: {len(zeros_app3)}")

print("\n" + "="*80)
