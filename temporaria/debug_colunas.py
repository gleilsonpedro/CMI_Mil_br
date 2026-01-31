import pandas as pd

# Verificar TO NV
print("="*60)
print("VERIFICANDO TO NV")
print("="*60)

xls = pd.read_excel('data/input/CMI-Mil.ods', sheet_name='TO NV', engine='odf')

for i in range(5):
    print(f"\nLinha {i}:")
    valores = xls.iloc[i].tolist()[:15]
    print(valores)

print("\n\nVerificando linha 2 (cabeçalho) em detalhe:")
linha2 = xls.iloc[2].tolist()
for i, val in enumerate(linha2[:12]):
    print(f"Coluna {i}: tipo={type(val).__name__:10s} | valor={repr(val)}")
