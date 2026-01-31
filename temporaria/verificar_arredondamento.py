"""
Verifica valores em cmi_app3 e cmi-mil_app3 (após arredondamento)
"""
import json

# cmi_app3
with open('data/output/cmi_app3/CE.json', 'r', encoding='utf-8') as f:
    cmi_app3 = json.load(f)

# cmi-mil_app3
with open('data/output/cmi-mil_app3/CE.json', 'r', encoding='utf-8') as f:
    cmi_mil_app3 = json.load(f)

# Filtra Fortaleza
fortaleza_cmi = [item for item in cmi_app3 if item.get('Municipio') == 'FORTALEZA']
fortaleza_mil = [item for item in cmi_mil_app3 if item.get('Municipio') == 'FORTALEZA']

print("="*80)
print("FORTALEZA - cmi_app3 (após arredondamento):")
print("="*80)
for item in sorted(fortaleza_cmi, key=lambda x: x['Ano'])[:10]:
    print(f"  {item['Ano']}: {item['Valor']}")

print("\n" + "="*80)
print("FORTALEZA - cmi-mil_app3 (após arredondamento):")
print("="*80)
for item in sorted(fortaleza_mil, key=lambda x: x['Ano'])[:10]:
    print(f"  {item['Ano']}: {item['Valor']}")

print("\n" + "="*80)
print("COMPARAÇÃO:")
print("="*80)
for cmi, mil in zip(sorted(fortaleza_cmi, key=lambda x: x['Ano'])[:10], 
                    sorted(fortaleza_mil, key=lambda x: x['Ano'])[:10]):
    diff = abs(cmi['Valor'] - mil['Valor'])
    print(f"  {cmi['Ano']}: CMI={cmi['Valor']} | CMI-Mil={mil['Valor']} | Diff={diff}")
