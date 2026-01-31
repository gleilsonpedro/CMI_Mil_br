"""
Verificação rápida dos dados de Abreulandia nos JSONs do app3
"""
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

print("="*80)
print("VERIFICAÇÃO FINAL - Dados nos JSONs do APP3")
print("="*80)

# CMI
json_cmi = BASE_DIR / 'data' / 'output' / 'cmi_app3' / 'TO.json'
with open(json_cmi, 'r', encoding='utf-8') as f:
    dados_cmi = json.load(f)

abreu_cmi = [r for r in dados_cmi if 'ABREU' in r['Municipio'].upper()]
abreu_cmi_sorted = sorted(abreu_cmi, key=lambda x: x['Ano'])

print(f"\n1. CMI - Abreulandia ({len(abreu_cmi)} registros):")
print("   Anos 2000-2005:")
for r in abreu_cmi_sorted:
    if 2000 <= r['Ano'] <= 2005:
        print(f"     {r['Ano']}: {r['Valor']}")

# CMI-Mil
json_cmi_mil = BASE_DIR / 'data' / 'output' / 'cmi-mil_app3' / 'TO.json'
with open(json_cmi_mil, 'r', encoding='utf-8') as f:
    dados_cmi_mil = json.load(f)

abreu_cmi_mil = [r for r in dados_cmi_mil if 'ABREU' in r['Municipio'].upper()]
abreu_cmi_mil_sorted = sorted(abreu_cmi_mil, key=lambda x: x['Ano'])

print(f"\n2. CMI-Mil - Abreulandia ({len(abreu_cmi_mil)} registros):")
print("   Anos 2000-2005:")
for r in abreu_cmi_mil_sorted:
    if 2000 <= r['Ano'] <= 2005:
        print(f"     {r['Ano']}: {r['Valor']}")

print("\n" + "="*80)
print("✓ Se os valores acima estão corretos, o problema está no cache do Streamlit")
print("✓ Clique no botão '🔄 Recarregar Dados' na sidebar do app")
print("="*80)
