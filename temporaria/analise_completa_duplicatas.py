"""
Identifica municípios com valores MUITO PRÓXIMOS entre CMI e CMI-Mil
em TODOS os anos (ou quase todos), indicando possível erro nas planilhas originais.
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

print("="*100)
print("IDENTIFICANDO MUNICÍPIOS COM CMI ≈ CMI-MIL EM TODOS OS ANOS")
print("="*100)
print("\nCritério: Diferença absoluta média < 0.03 E diferença máxima < 0.10")
print("Isso indica que os valores são praticamente idênticos em todos os anos.\n")

municipios_suspeitos = []

for uf in UFS:
    # Carrega dados
    with open(DIR_CMI / f'{uf}.json', 'r', encoding='utf-8') as f:
        cmi = pd.DataFrame(json.load(f))
    
    with open(DIR_CMI_MIL / f'{uf}.json', 'r', encoding='utf-8') as f:
        cmi_mil = pd.DataFrame(json.load(f))
    
    # Merge por município e ano
    merged = pd.merge(
        cmi[['Municipio', 'Ano', 'Valor']], 
        cmi_mil[['Municipio', 'Ano', 'Valor']], 
        on=['Municipio', 'Ano'],
        suffixes=('_cmi', '_mil')
    )
    
    # Calcula diferença absoluta
    merged['Diferenca_Abs'] = abs(merged['Valor_cmi'] - merged['Valor_mil'])
    
    # Agrupa por município
    for municipio in merged['Municipio'].unique():
        dados_mun = merged[merged['Municipio'] == municipio]
        
        # Estatísticas da diferença
        diff_media = dados_mun['Diferenca_Abs'].mean()
        diff_max = dados_mun['Diferenca_Abs'].max()
        diff_min = dados_mun['Diferenca_Abs'].min()
        total_anos = len(dados_mun)
        anos_identicos = (dados_mun['Diferenca_Abs'] < 0.01).sum()
        percentual_identicos = (anos_identicos / total_anos) * 100
        
        # Critério: diferença média muito pequena E diferença máxima também pequena
        # Isso indica que TODOS os anos estão praticamente iguais
        if diff_media < 0.03 and diff_max < 0.10:
            cmi_media = dados_mun['Valor_cmi'].mean()
            cmi_mil_media = dados_mun['Valor_mil'].mean()
            
            municipios_suspeitos.append({
                'UF': uf,
                'Municipio': municipio,
                'Total_Anos': total_anos,
                'Anos_Identicos': anos_identicos,
                'Percent_Identicos': round(percentual_identicos, 1),
                'Diff_Media': round(diff_media, 3),
                'Diff_Max': round(diff_max, 3),
                'Diff_Min': round(diff_min, 3),
                'CMI_Media': round(cmi_media, 2),
                'CMI_Mil_Media': round(cmi_mil_media, 2)
            })

# Converte para DataFrame e ordena
df_suspeitos = pd.DataFrame(municipios_suspeitos).sort_values(['Diff_Media', 'Diff_Max'])

print(f"TOTAL DE MUNICÍPIOS SUSPEITOS: {len(df_suspeitos)}")
print("="*100)
print("\n📊 RANKING DOS 50 MUNICÍPIOS MAIS SUSPEITOS:\n")

# Formata saída
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 200)
pd.set_option('display.max_rows', None)

print(df_suspeitos.head(50).to_string(index=False))

# Salva arquivo completo
arquivo_saida = BASE_DIR / 'temporaria' / 'municipios_suspeitos_duplicados.csv'
df_suspeitos.to_csv(arquivo_saida, index=False, encoding='utf-8-sig')
print(f"\n\n💾 Lista completa salva em: {arquivo_saida.relative_to(BASE_DIR)}")

# Análise por UF
print("\n" + "="*100)
print("ANÁLISE POR UF:")
print("="*100)
analise_uf = df_suspeitos.groupby('UF').size().sort_values(ascending=False)
for uf, count in analise_uf.items():
    # Conta total de municípios da UF
    with open(DIR_CMI / f'{uf}.json', 'r', encoding='utf-8') as f:
        total_mun = len(pd.DataFrame(json.load(f))['Municipio'].unique())
    percentual = (count / total_mun * 100) if total_mun > 0 else 0
    print(f"  {uf}: {count:3d} municípios suspeitos de {total_mun:3d} ({percentual:.1f}%)")

print("\n" + "="*100)
print("CONCLUSÃO:")
print("="*100)
print("Estes municípios apresentam valores praticamente IDÊNTICOS entre CMI e CMI-Mil")
print("em todos (ou quase todos) os anos. Isso sugere que:")
print("  1. As planilhas originais podem ter valores duplicados/copiados incorretamente, OU")
print("  2. Os cálculos na planilha estão usando a mesma fórmula para ambos, OU")
print("  3. Há um problema na extração dos dados")
print("\nCMI e CMI-Mil usam metodologias DIFERENTES e NÃO DEVERIAM ter valores idênticos.")
print("="*100)
