"""
Script para corrigir os JSONs em cmi_app3 e cmi-mil_app3
Copia de CMI_puro e CMI_MIL mantendo TODOS os registros (inclusive zeros)
Adiciona campo Codigo_Municipio extraindo do nome do município
"""
import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DIR_CMI_PURO = BASE_DIR / 'data' / 'output' / 'CMI_puro'
DIR_CMI_MIL = BASE_DIR / 'data' / 'output' / 'CMI_MIL'
DIR_CMI_APP3 = BASE_DIR / 'data' / 'output' / 'cmi_app3'
DIR_CMI_MIL_APP3 = BASE_DIR / 'data' / 'output' / 'cmi-mil_app3'

def extrair_codigo_municipio(nome_municipio):
    """
    Extrai código do município se estiver no formato '170025 ABREULANDIA'
    Retorna código ou None
    """
    match = re.match(r'^(\d{6,7})\s+', str(nome_municipio))
    if match:
        return match.group(1)
    return None

def limpar_nome_municipio(nome_municipio):
    """
    Remove código do início do nome
    '170025 ABREULANDIA' -> 'ABREULANDIA'
    """
    nome_limpo = re.sub(r'^\d{6,7}\s+', '', str(nome_municipio))
    return nome_limpo.strip()

def processar_json(arquivo_origem, arquivo_destino, tipo_cmi):
    """
    Processa um arquivo JSON:
    - Adiciona campo Codigo_Municipio
    - Limpa nome do município
    - Mantém TODOS os registros (inclusive zeros)
    - Muda o tipo de CMI_puro/CMI_MIL para CMI/CMI-Mil
    """
    print(f"  Processando: {arquivo_origem.name}")
    
    with open(arquivo_origem, 'r', encoding='utf-8') as f:
        dados = json.load(f)
    
    # Processar cada registro
    dados_processados = []
    for registro in dados:
        # Extrair código
        codigo = extrair_codigo_municipio(registro['Municipio'])
        
        # Limpar nome
        nome_limpo = limpar_nome_municipio(registro['Municipio'])
        
        # Criar novo registro
        novo_registro = {
            'Municipio': nome_limpo,
            'Codigo_Municipio': codigo,
            'Ano': registro['Ano'],
            'Valor': round(registro['Valor'], 2),  # Arredondar para 2 casas decimais
            'UF': registro['UF'],
            'Tipo': tipo_cmi
        }
        
        dados_processados.append(novo_registro)
    
    # Salvar
    arquivo_destino.parent.mkdir(parents=True, exist_ok=True)
    with open(arquivo_destino, 'w', encoding='utf-8') as f:
        json.dump(dados_processados, f, ensure_ascii=False, indent=2)
    
    print(f"    ✓ Salvo: {len(dados_processados)} registros")
    return len(dados_processados)

# MAIN
print("="*80)
print("CORRIGINDO JSONS - Mantendo TODOS os registros")
print("="*80)

# 1. Processar CMI_puro -> cmi_app3
print("\n1. Processando CMI_puro -> cmi_app3...")
total_cmi = 0
for arquivo in sorted(DIR_CMI_PURO.glob('*.json')):
    arquivo_destino = DIR_CMI_APP3 / arquivo.name
    total_cmi += processar_json(arquivo, arquivo_destino, 'CMI')

print(f"\n  Total de registros CMI: {total_cmi}")

# 2. Processar CMI_MIL -> cmi-mil_app3
print("\n2. Processando CMI_MIL -> cmi-mil_app3...")
total_cmi_mil = 0
for arquivo in sorted(DIR_CMI_MIL.glob('*.json')):
    arquivo_destino = DIR_CMI_MIL_APP3 / arquivo.name
    total_cmi_mil += processar_json(arquivo, arquivo_destino, 'CMI-Mil')

print(f"\n  Total de registros CMI-Mil: {total_cmi_mil}")

print("\n" + "="*80)
print("CORREÇÃO CONCLUÍDA!")
print("="*80)
print("\nOs JSONs agora contêm TODOS os anos, inclusive aqueles com valor 0.")
print("Isso garante que não haja desalinhamento entre anos e valores.")
