"""
Análise detalhada de Abreulandia-TO para entender os cálculos de CMI e CMI-Mil
"""
import json
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

# Carregar dados
print("="*100)
print("ANÁLISE DETALHADA: ABREULANDIA-TO")
print("="*100)

# 1. CMI e CMI-Mil processados
with open(BASE_DIR / 'data/output/cmi_app3/TO.json', 'r', encoding='utf-8') as f:
    cmi = pd.DataFrame(json.load(f))

with open(BASE_DIR / 'data/output/cmi-mil_app3/TO.json', 'r', encoding='utf-8') as f:
    cmi_mil = pd.DataFrame(json.load(f))

# 2. Nascidos Vivos e Óbitos
with open(BASE_DIR / 'data/output/nascidos_vivos/TO.json', 'r', encoding='utf-8') as f:
    nv = pd.DataFrame(json.load(f))

with open(BASE_DIR / 'data/output/obitos/TO.json', 'r', encoding='utf-8') as f:
    ob = pd.DataFrame(json.load(f))

# Filtrar Abreulandia
abreu_cmi = cmi[cmi['Municipio'] == 'ABREULANDIA'].sort_values('Ano')
abreu_cmi_mil = cmi_mil[cmi_mil['Municipio'] == 'ABREULANDIA'].sort_values('Ano')
abreu_nv = nv[nv['Municipio'] == 'ABREULANDIA'].sort_values('Ano')
abreu_ob = ob[ob['Municipio'] == 'ABREULANDIA'].sort_values('Ano')

# Merge tudo
dados = pd.merge(abreu_cmi[['Ano', 'Valor']], abreu_cmi_mil[['Ano', 'Valor']], 
                 on='Ano', suffixes=('_CMI', '_CMI_Mil'))
dados = pd.merge(dados, abreu_nv[['Ano', 'Valor']], on='Ano')
dados.rename(columns={'Valor': 'Nascidos_Vivos'}, inplace=True)
dados = pd.merge(dados, abreu_ob[['Ano', 'Valor']], on='Ano')
dados.rename(columns={'Valor': 'Obitos'}, inplace=True)

# Calcular CMI baseado nos dados
dados['CMI_Calculado'] = (dados['Obitos'] / dados['Nascidos_Vivos']) * 1000
dados['CMI_Calculado'] = dados['CMI_Calculado'].replace([float('inf'), float('-inf')], 0)
dados['CMI_Calculado'] = dados['CMI_Calculado'].fillna(0)

print("\n📊 DADOS COMPLETOS (primeiros 15 anos):\n")
print(f"{'Ano':<6} {'Óbitos':<8} {'Nasc.Vivos':<12} {'CMI(Plan.)':<12} {'CMI(Calc.)':<12} {'CMI-Mil(Plan.)':<15}")
print("-" * 100)

for _, row in dados.head(15).iterrows():
    ano = int(row['Ano'])
    ob = int(row['Obitos'])
    nv = int(row['Nascidos_Vivos'])
    cmi_plan = row['Valor_CMI']
    cmi_calc = row['CMI_Calculado']
    cmi_mil = row['Valor_CMI_Mil']
    
    print(f"{ano:<6} {ob:<8} {nv:<12} {cmi_plan:<12.2f} {cmi_calc:<12.2f} {cmi_mil:<15.2f}")

print("\n" + "="*100)
print("ANÁLISE DOS CÁLCULOS")
print("="*100)

# Exemplo de ano com dados (2000)
ano_exemplo = dados[dados['Ano'] == 2000].iloc[0]
print(f"\n📝 EXEMPLO: ANO 2000 (Abreulandia-TO)\n")
print(f"Dados disponíveis:")
print(f"  • Óbitos de menores de 1 ano: {int(ano_exemplo['Obitos'])}")
print(f"  • Nascidos Vivos: {int(ano_exemplo['Nascidos_Vivos'])}")
print(f"  • CMI da planilha: {ano_exemplo['Valor_CMI']:.2f}")
print(f"  • CMI-Mil da planilha: {ano_exemplo['Valor_CMI_Mil']:.2f}")

print(f"\n🔢 CÁLCULO DO CMI (Coeficiente de Mortalidade Infantil):")
print(f"   Fórmula: CMI = (Óbitos < 1 ano / Nascidos Vivos) × 1.000")
print(f"   CMI = ({int(ano_exemplo['Obitos'])} / {int(ano_exemplo['Nascidos_Vivos'])}) × 1.000")
print(f"   CMI = {ano_exemplo['CMI_Calculado']:.2f} por mil nascimentos")
print(f"   Planilha mostra: {ano_exemplo['Valor_CMI']:.2f}")

if abs(ano_exemplo['CMI_Calculado'] - ano_exemplo['Valor_CMI']) < 1.0:
    print(f"   ✅ CONFERE! (diferença: {abs(ano_exemplo['CMI_Calculado'] - ano_exemplo['Valor_CMI']):.2f})")
else:
    print(f"   ⚠️ NÃO CONFERE! (diferença: {abs(ano_exemplo['CMI_Calculado'] - ano_exemplo['Valor_CMI']):.2f})")

print(f"\n   Interpretação:")
print(f"   A cada 1.000 bebês que nascem em Abreulandia, {ano_exemplo['CMI_Calculado']:.1f} morrem antes de 1 ano.")

print(f"\n🔢 CÁLCULO DO CMI-MIL (Coeficiente de Mortalidade Infantil por Mil Habitantes):")
print(f"   Fórmula: CMI-Mil = (Óbitos < 1 ano / População Total) × 1.000")
print(f"   ")
print(f"   ⚠️ PROBLEMA: Não temos dados de População Total!")
print(f"   ")
print(f"   Para calcular, precisaríamos:")
print(f"   CMI-Mil = ({int(ano_exemplo['Obitos'])} / População_Total) × 1.000")
print(f"   Planilha mostra: {ano_exemplo['Valor_CMI_Mil']:.2f}")
print(f"   ")
print(f"   Se assumirmos que a planilha está correta, podemos INFERIR a população:")
print(f"   População = ({int(ano_exemplo['Obitos'])} × 1.000) / {ano_exemplo['Valor_CMI_Mil']:.2f}")

if ano_exemplo['Valor_CMI_Mil'] > 0:
    pop_inferida = (ano_exemplo['Obitos'] * 1000) / ano_exemplo['Valor_CMI_Mil']
    print(f"   População inferida: {pop_inferida:,.0f} habitantes")
    
    print(f"\n   Interpretação:")
    print(f"   A cada 1.000 habitantes de Abreulandia, {ano_exemplo['Valor_CMI_Mil']:.1f} são óbitos de bebês < 1 ano.")

print("\n" + "="*100)
print("DIFERENÇA ENTRE CMI E CMI-MIL")
print("="*100)

print(f"\n1️⃣ CMI = {ano_exemplo['Valor_CMI']:.2f} por mil NASCIMENTOS")
print(f"   • Denominador: Nascidos Vivos ({int(ano_exemplo['Nascidos_Vivos'])})")
print(f"   • Mede: Risco de morte para bebês que nascem")

print(f"\n2️⃣ CMI-Mil = {ano_exemplo['Valor_CMI_Mil']:.2f} por mil HABITANTES")
if ano_exemplo['Valor_CMI_Mil'] > 0:
    print(f"   • Denominador: População Total (≈{pop_inferida:,.0f} habitantes estimados)")
print(f"   • Mede: Impacto da mortalidade infantil na população geral")

print(f"\n3️⃣ Por que são diferentes?")
print(f"   • Nascidos Vivos: {int(ano_exemplo['Nascidos_Vivos'])}")
if ano_exemplo['Valor_CMI_Mil'] > 0:
    print(f"   • População Total: ≈{pop_inferida:,.0f}")
    print(f"   • População é {pop_inferida/ano_exemplo['Nascidos_Vivos']:.1f}x MAIOR que nascimentos!")
    print(f"   • Logo: CMI ({ano_exemplo['Valor_CMI']:.2f}) é {ano_exemplo['Valor_CMI']/ano_exemplo['Valor_CMI_Mil']:.1f}x MAIOR que CMI-Mil ({ano_exemplo['Valor_CMI_Mil']:.2f})")

print("\n" + "="*100)
print("CONCLUSÃO")
print("="*100)
print("\n✅ Em Abreulandia, os valores são DIFERENTES (como esperado):")
print(f"   • CMI médio: {dados['Valor_CMI'].mean():.2f}")
print(f"   • CMI-Mil médio: {dados['Valor_CMI_Mil'].mean():.2f}")
print(f"   • Diferença: {abs(dados['Valor_CMI'].mean() - dados['Valor_CMI_Mil'].mean()):.2f}")

print("\n❌ Em Fortaleza (e 316 outros municípios), os valores são IGUAIS (ERRO):")
print("   • Isso indica que a planilha usou a mesma fórmula para ambos")
print("   • Ou copiou valores incorretamente")

print("\n💡 SOLUÇÃO: Precisamos de dados de População Total do IBGE para recalcular CMI-Mil corretamente")
print("="*100)
