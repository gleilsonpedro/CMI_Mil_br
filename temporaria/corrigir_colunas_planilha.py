"""
Script para corrigir colunas '#Mun', 'Inic', 'Fim' na planilha CMI-Mil.ods
Substitui por 1998, 1999, 2000 respectivamente
"""
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
ARQUIVO_ORIGINAL = BASE_DIR / 'data' / 'input' / 'CMI-Mil.ods'
ARQUIVO_BACKUP = BASE_DIR / 'data' / 'input' / 'CMI-Mil_backup_antes_correcao.ods'

def corrigir_abas():
    print("="*80)
    print("🔧 CORREÇÃO DE COLUNAS NA PLANILHA CMI-Mil.ods")
    print("="*80)
    
    # Fazer backup
    print(f"\n📦 Criando backup: {ARQUIVO_BACKUP.name}")
    import shutil
    shutil.copy2(ARQUIVO_ORIGINAL, ARQUIVO_BACKUP)
    print("   ✓ Backup criado")
    
    # Ler todas as abas
    print(f"\n📂 Carregando planilha...")
    xls = pd.read_excel(ARQUIVO_ORIGINAL, sheet_name=None, engine='odf')
    print(f"   ✓ {len(xls)} abas carregadas")
    
    abas_corrigidas = []
    abas_sem_alteracao = []
    
    print("\n" + "="*80)
    print("🔍 VERIFICANDO E CORRIGINDO ABAS")
    print("="*80)
    
    for nome_aba, df_aba in xls.items():
        # Verificar se é aba NV ou OB
        nome_upper = nome_aba.upper().strip()
        if not (' NV' in nome_upper or ' OB' in nome_upper):
            continue
        
        # Verificar todas as linhas em busca de '#Mun', 'Inic', 'Fim'
        alterou = False
        for idx in range(min(5, len(df_aba))):  # Verificar primeiras 5 linhas
            linha = df_aba.iloc[idx].tolist()
            
            if '#Mun' in linha or 'Inic' in linha or 'Fim' in linha:
                if not alterou:
                    print(f"\n  📋 {nome_aba} (linha {idx})")
                    alterou = True
                
                # Corrigir valores na linha
                nova_linha = []
                for val in linha:
                    if val == '#Mun':
                        nova_linha.append(1998)
                        print(f"     ✓ '#Mun' → 1998")
                    elif val == 'Inic':
                        nova_linha.append(1999)
                        print(f"     ✓ 'Inic' → 1999")
                    elif val == 'Fim':
                        nova_linha.append(2000)
                        print(f"     ✓ 'Fim' → 2000")
                    else:
                        nova_linha.append(val)
                
                # Atualizar a linha no DataFrame
                df_aba.iloc[idx] = nova_linha
        
        if alterou:
            xls[nome_aba] = df_aba
            abas_corrigidas.append(nome_aba)
        else:
            abas_sem_alteracao.append(nome_aba)
    
    # Salvar planilha corrigida
    if abas_corrigidas:
        print("\n" + "="*80)
        print("💾 SALVANDO PLANILHA CORRIGIDA")
        print("="*80)
        
        with pd.ExcelWriter(ARQUIVO_ORIGINAL, engine='odf') as writer:
            for nome_aba, df in xls.items():
                df.to_excel(writer, sheet_name=nome_aba, index=False, header=False)
        
        print(f"   ✓ Planilha salva: {ARQUIVO_ORIGINAL}")
    
    # Resumo
    print("\n" + "="*80)
    print("✅ CORREÇÃO CONCLUÍDA")
    print("="*80)
    print(f"  📝 Abas corrigidas: {len(abas_corrigidas)}")
    if abas_corrigidas:
        for aba in abas_corrigidas[:10]:
            print(f"     • {aba}")
        if len(abas_corrigidas) > 10:
            print(f"     ... e mais {len(abas_corrigidas) - 10} abas")
    
    print(f"\n  ✓ Abas NV/OB sem alteração: {len([a for a in abas_sem_alteracao if ' NV' in a.upper() or ' OB' in a.upper()])}")
    print(f"  💾 Backup salvo em: {ARQUIVO_BACKUP.name}")
    print("="*80)

if __name__ == "__main__":
    corrigir_abas()
