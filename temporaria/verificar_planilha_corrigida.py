"""
Script para verificar a estrutura da planilha CMI-Mil.ods após correção
"""
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
ARQUIVO_CMI_MIL = BASE_DIR / 'data' / 'input' / 'CMI-Mil.ods'

print("="*80)
print("VERIFICAÇÃO DA PLANILHA CMI-Mil.ods (APÓS CORREÇÃO)")
print("="*80)

# Ler aba CMI-Mil TO
try:
    df = pd.read_excel(ARQUIVO_CMI_MIL, sheet_name='CMI-Mil TO', engine='odf', header=None)
    
    print("\n1. Estrutura da aba 'CMI-Mil TO':")
    print(f"   Dimensões: {df.shape}")
    
    # Procurar linha do cabeçalho
    linha_cabecalho = None
    for i, row in df.iterrows():
        linha_texto = row.astype(str).tolist()
        if any('munic' in str(cell).lower() for cell in linha_texto):
            linha_cabecalho = i
            print(f"\n   Cabeçalho encontrado na linha: {linha_cabecalho}")
            print(f"   Primeiras 15 colunas do cabeçalho:")
            for j, col in enumerate(linha_texto[:15]):
                print(f"     Col {j}: {col}")
            break
    
    # Verificar se tem os anos 1998, 1999, 2000
    if linha_cabecalho is not None:
        cabecalho = df.iloc[linha_cabecalho].tolist()
        anos_procurados = ['1998', '1999', '2000', 1998, 1999, 2000, 1998.0, 1999.0, 2000.0]
        
        print("\n2. Verificando anos 1998, 1999, 2000:")
        for ano in [1998, 1999, 2000]:
            encontrado = False
            for col_val in cabecalho:
                try:
                    if float(col_val) == ano:
                        encontrado = True
                        break
                except:
                    if str(col_val) == str(ano):
                        encontrado = True
                        break
            
            if encontrado:
                print(f"   ✓ Ano {ano}: ENCONTRADO")
            else:
                print(f"   ✗ Ano {ano}: NÃO ENCONTRADO")
        
        # Verificar se ainda tem #Mun, Inic, Fim
        textos_antigos = ['#MUN', '#Mun', 'INIC', 'Inic', 'FIM', 'Fim']
        print("\n3. Verificando se ainda existem colunas antigas (#Mun, Inic, Fim):")
        tem_antigos = False
        for texto in textos_antigos:
            for col_val in cabecalho:
                if str(col_val).upper() == texto.upper():
                    print(f"   ⚠️  '{texto}': AINDA EXISTE")
                    tem_antigos = True
        
        if not tem_antigos:
            print("   ✓ Nenhuma coluna antiga encontrada")
        
        # Mostrar dados de Abreulandia
        df_com_header = pd.read_excel(ARQUIVO_CMI_MIL, sheet_name='CMI-Mil TO', engine='odf', header=linha_cabecalho)
        
        print("\n4. Dados de ABREULANDIA:")
        for col in df_com_header.columns:
            col_values = df_com_header[col].astype(str).str.upper()
            if col_values.str.contains('ABREU', na=False).any():
                linha_idx = col_values[col_values.str.contains('ABREU', na=False)].index[0]
                linha_abreu = df_com_header.iloc[linha_idx]
                
                print(f"   Município: {linha_abreu.iloc[0]}")
                print(f"\n   Anos 1996-2005:")
                for ano in range(1996, 2006):
                    try:
                        if ano in df_com_header.columns:
                            valor = linha_abreu[ano]
                            print(f"     {ano}: {valor}")
                        elif float(ano) in df_com_header.columns:
                            valor = linha_abreu[float(ano)]
                            print(f"     {ano}: {valor}")
                    except:
                        pass
                break
    
    print("\n" + "="*80)
    print("CONCLUSÃO:")
    print("="*80)
    print("Se os anos 1998, 1999, 2000 estão presentes e as colunas antigas")
    print("(#Mun, Inic, Fim) não existem mais, a planilha está OK para raspagem!")
    print("="*80)
    
except Exception as e:
    print(f"\n❌ Erro ao ler planilha: {e}")
    import traceback
    traceback.print_exc()
