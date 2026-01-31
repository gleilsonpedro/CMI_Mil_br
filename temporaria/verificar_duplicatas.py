"""
Script para verificar se há duplicatas em CMI_MIL original
"""
import json
from pathlib import Path
from collections import Counter

BASE_DIR = Path(__file__).parent.parent
json_cmi_mil = BASE_DIR / 'data' / 'output' / 'CMI_MIL' / 'TO.json'

print("="*80)
print("VERIFICANDO DUPLICATAS EM CMI_MIL/TO.json")
print("="*80)

with open(json_cmi_mil, 'r', encoding='utf-8') as f:
    dados = json.load(f)

# Filtrar Abreulandia
abreu = [r for r in dados if 'ABREU' in r['Municipio'].upper()]
print(f"\nTotal de registros de Abreulandia: {len(abreu)}")

# Verificar duplicatas por ano
anos = [r['Ano'] for r in abreu]
contagem = Counter(anos)

print("\nContagem de registros por ano:")
for ano in sorted(contagem.keys()):
    count = contagem[ano]
    if count > 1:
        print(f"  {ano}: {count} registros ⚠️ DUPLICADO")
        # Mostrar os valores duplicados
        valores = [r['Valor'] for r in abreu if r['Ano'] == ano]
        print(f"       Valores: {valores}")
    else:
        print(f"  {ano}: {count} registro")

# Verificar estrutura completa
print(f"\nPrimeiros 5 registros de Abreulandia:")
for r in sorted(abreu, key=lambda x: x['Ano'])[:5]:
    print(f"  {r}")

print("\n" + "="*80)
