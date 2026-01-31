"""
Script para listar todas as abas das planilhas ODS
"""
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
ARQUIVO_CMI = BASE_DIR / 'data' / 'input' / 'CMI.ods'
ARQUIVO_CMI_MIL = BASE_DIR / 'data' / 'input' / 'CMI-Mil.ods'

print("="*80)
print("LISTANDO ABAS DAS PLANILHAS ODS")
print("="*80)

# 1. CMI.ods
print("\n1. Abas em CMI.ods:")
try:
    xls = pd.read_excel(ARQUIVO_CMI, sheet_name=None, engine='odf')
    abas = list(xls.keys())
    print(f"   Total de abas: {len(abas)}")
    for i, aba in enumerate(abas, 1):
        print(f"   {i}. {aba}")
except Exception as e:
    print(f"   ❌ Erro: {e}")

# 2. CMI-Mil.ods
print("\n2. Abas em CMI-Mil.ods:")
try:
    xls_mil = pd.read_excel(ARQUIVO_CMI_MIL, sheet_name=None, engine='odf')
    abas_mil = list(xls_mil.keys())
    print(f"   Total de abas: {len(abas_mil)}")
    for i, aba in enumerate(abas_mil, 1):
        print(f"   {i}. {aba}")
except Exception as e:
    print(f"   ❌ Erro: {e}")

print("\n" + "="*80)
