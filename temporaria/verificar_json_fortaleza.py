"""
Verifica os valores de Fortaleza nos JSONs processados
"""
import json

# Lê CE.json de CMI_puro
with open('data/output/CMI_puro/CE.json', 'r', encoding='utf-8') as f:
    cmi_puro = json.load(f)

# Lê CE.json de CMI_MIL
with open('data/output/CMI_MIL/CE.json', 'r', encoding='utf-8') as f:
    cmi_mil = json.load(f)

# Filtra Fortaleza
fortaleza_cmi = [item for item in cmi_puro if 'FORTALEZA' in item.get('Municipio', '').upper()]
fortaleza_mil = [item for item in cmi_mil if 'FORTALEZA' in item.get('Municipio', '').upper()]

print("="*80)
print("FORTALEZA - CMI_puro (CMI.ods):")
print("="*80)
for item in sorted(fortaleza_cmi, key=lambda x: x['Ano'])[:10]:
    print(f"  {item['Ano']}: {item['Valor']}")

print("\n" + "="*80)
print("FORTALEZA - CMI_MIL (CMI-Mil.ods):")
print("="*80)
for item in sorted(fortaleza_mil, key=lambda x: x['Ano'])[:10]:
    print(f"  {item['Ano']}: {item['Valor']}")
