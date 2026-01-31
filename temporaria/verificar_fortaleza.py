import pandas as pd
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DIR_CMI = BASE_DIR / 'data' / 'output' / 'cmi_app3'
DIR_CMI_MIL = BASE_DIR / 'data' / 'output' / 'cmi-mil_app3'

# Carregar CMI
with open(DIR_CMI / 'CE.json', 'r', encoding='utf-8') as f:
    dados_cmi = json.load(f)

# Carregar CMI-Mil
with open(DIR_CMI_MIL / 'CE.json', 'r', encoding='utf-8') as f:
    dados_cmi_mil = json.load(f)

# Filtrar Fortaleza
df_cmi = pd.DataFrame(dados_cmi)
df_cmi_mil = pd.DataFrame(dados_cmi_mil)

fortaleza_cmi = df_cmi[df_cmi['Municipio'] == 'FORTALEZA'].sort_values('Ano')
fortaleza_cmi_mil = df_cmi_mil[df_cmi_mil['Municipio'] == 'FORTALEZA'].sort_values('Ano')

# Merge para comparar
comparacao = pd.merge(
    fortaleza_cmi[['Ano', 'Valor']],
    fortaleza_cmi_mil[['Ano', 'Valor']],
    on='Ano',
    suffixes=('_CMI', '_CMI_MIL')
)

print("="*60)
print("FORTALEZA - CE: CMI vs CMI-Mil")
print("="*60)
print(f"\n{'Ano':<8} {'CMI':>10} {'CMI-Mil':>12} {'Diferença':>12}")
print("-"*60)

for _, row in comparacao.iterrows():
    diff = row['Valor_CMI'] - row['Valor_CMI_MIL']
    print(f"{int(row['Ano']):<8} {row['Valor_CMI']:>10.2f} {row['Valor_CMI_MIL']:>12.2f} {diff:>12.2f}")

print("-"*60)
print(f"\nTotal de registros: {len(comparacao)}")
print(f"CMI Média: {comparacao['Valor_CMI'].mean():.2f}")
print(f"CMI-Mil Média: {comparacao['Valor_CMI_MIL'].mean():.2f}")
print(f"Diferença Média: {(comparacao['Valor_CMI'] - comparacao['Valor_CMI_MIL']).mean():.2f}")
print("="*60)
