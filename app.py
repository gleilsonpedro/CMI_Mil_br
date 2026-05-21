"""
Dashboard de Análise de Indicadores de Saúde Municipal
CMI, CMI-Mil, Nascidos Vivos e Óbitos
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import json
from pathlib import Path
import numpy as np

# Configuração da página
st.set_page_config(
    page_title="Análise de Saúde Municipal",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Diretórios de dados
BASE_DIR = Path(__file__).parent
DIR_CMI = BASE_DIR / 'data' / 'output' / 'cmi_app3'
DIR_CMI_MIL = BASE_DIR / 'data' / 'output' / 'cmi-mil_app3'
DIR_NV = BASE_DIR / 'data' / 'output' / 'nascidos_vivos'
DIR_OB = BASE_DIR / 'data' / 'output' / 'obitos'
DIR_FORTALEZA = BASE_DIR / 'data' / 'output' / 'fortaleza'

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.8rem;
        font-weight: 600;
        color: #ffffff;
        padding: 1rem 0;
        border-bottom: 3px solid #3498db;
        margin: 2rem 0 1rem 0;
    }
    .info-box {
        background-color: #1e1e1e;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #3498db;
        margin: 1rem 0;
        color: #e0e0e0;
    }
    .explanation-box {
        background-color: #262626;
        padding: 1.2rem;
        border-radius: 8px;
        border-left: 4px solid #3498db;
        margin: 1rem 0;
        font-size: 0.95rem;
        color: #e0e0e0;
        line-height: 1.6;
    }
    .explanation-box b {
        color: #64b5f6;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300)
def carregar_dados_por_tipo(tipo):
    """Carrega dados de um tipo específico (CMI, CMI_MIL, NV, OB)"""
    if tipo == 'CMI':
        diretorio = DIR_CMI
    elif tipo == 'CMI_MIL':
        diretorio = DIR_CMI_MIL
    elif tipo == 'NV':
        diretorio = DIR_NV
    elif tipo == 'OB':
        diretorio = DIR_OB
    else:
        return pd.DataFrame()
    
    dados_list = []
    for arquivo in diretorio.glob('*.json'):
        with open(arquivo, 'r', encoding='utf-8') as f:
            dados = json.load(f)
            dados_list.extend(dados)
    
    return pd.DataFrame(dados_list) if dados_list else pd.DataFrame()


@st.cache_data(ttl=300)
def carregar_dados_fortaleza(tipo):
    """Carrega dados de Fortaleza por bairro."""
    arquivos = {
        'CMI': 'CMI.json',
        'CMI_MIL': 'CMI_MIL.json',
        'NV': 'NV.json',
        'OB': 'OB.json'
    }

    nome_arquivo = arquivos.get(tipo)
    if not nome_arquivo:
        return pd.DataFrame()

    arquivo = DIR_FORTALEZA / nome_arquivo
    if not arquivo.exists():
        return pd.DataFrame()

    with open(arquivo, 'r', encoding='utf-8') as f:
        dados = json.load(f)

    return pd.DataFrame(dados) if dados else pd.DataFrame()

@st.cache_data(ttl=300)
def obter_lista_municipios():
    """Obtém lista única de municípios com UF"""
    df_cmi = carregar_dados_por_tipo('CMI')
    if df_cmi.empty:
        return []
    municipios = df_cmi[['Municipio', 'UF']].drop_duplicates()
    municipios_lista = [f"{row['Municipio']} - {row['UF']}" for _, row in municipios.iterrows()]
    return sorted(municipios_lista)


@st.cache_data(ttl=300)
def obter_lista_bairros_fortaleza():
    """Obtém lista única de bairros de Fortaleza."""
    bairros = set()

    for tipo in ['CMI', 'CMI_MIL', 'NV', 'OB']:
        df = carregar_dados_fortaleza(tipo)
        if df.empty or 'Bairro' not in df.columns:
            continue

        for bairro in df['Bairro'].dropna().drop_duplicates():
            bairro_limpo = str(bairro).strip()
            if bairro_limpo:
                bairros.add(bairro_limpo)

    return sorted(bairros)

def criar_grafico_linha(df, titulo, cor='#1f77b4', yaxis_title='Valor'):
    """Cria gráfico de linha padronizado"""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['Ano'],
        y=df['Valor'],
        mode='lines+markers',
        name=titulo,
        line=dict(color=cor, width=3),
        marker=dict(size=8),
        hovertemplate='%{y:.1f}<extra></extra>'
    ))
    fig.update_layout(
        title=titulo,
        xaxis_title='Ano',
        yaxis_title=yaxis_title,
        hovermode='x unified',
        template='plotly_white',
        height=400
    )
    return fig

def criar_grafico_multiplos_municipios(dados_dict, tipo_indicador, titulo):
    """Cria gráfico com múltiplos municípios"""
    cores = px.colors.qualitative.Set2 + px.colors.qualitative.Pastel
    
    fig = go.Figure()
    for idx, (municipio, df) in enumerate(dados_dict.items()):
        if not df.empty:
            fig.add_trace(go.Scatter(
                x=df['Ano'],
                y=df['Valor'],
                mode='lines+markers',
                name=municipio,
                line=dict(color=cores[idx % len(cores)], width=2.5),
                marker=dict(size=7),
                hovertemplate='%{y:.1f}<extra></extra>'
            ))
    
    fig.update_layout(
        title=titulo,
        xaxis_title='Ano',
        yaxis_title=tipo_indicador,
        hovermode='x unified',
        template='plotly_white',
        height=500,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )
    return fig

def criar_grafico_comparacao(df1, df2, label1, label2, titulo):
    """Cria gráfico comparativo entre dois indicadores"""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df1['Ano'], y=df1['Valor'],
        mode='lines+markers',
        name=label1,
        line=dict(color='#1f77b4', width=3),
        hovertemplate='%{y:.1f}<extra></extra>'
    ))
    fig.add_trace(go.Scatter(
        x=df2['Ano'], y=df2['Valor'],
        mode='lines+markers',
        name=label2,
        line=dict(color='#ff7f0e', width=3),
        hovertemplate='%{y:.1f}<extra></extra>'
    ))
    fig.update_layout(
        title=titulo,
        xaxis_title='Ano',
        yaxis_title='Valor',
        hovermode='x unified',
        template='plotly_white',
        height=400,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )
    return fig

# Título principal
st.markdown('<h1 class="main-header">Análise CMI & CMI-Mil<br><small style="font-size: 0.6em; color: #7f8c8d;">Dashboard para Visualização de Coeficientes de Mortalidade Infantil</small></h1>', unsafe_allow_html=True)

# Sidebar - Seleção de municípios
with st.sidebar:
    st.title("Filtros")
    
    # Botão recarregar
    if st.button("Recarregar Dados", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    st.markdown("---")
    
    # Seleção de municípios (multiselect)
    municipios_disponiveis = obter_lista_municipios()
    if municipios_disponiveis:
        municipios_selecionados = st.multiselect(
            "Selecione os Municípios",
            options=municipios_disponiveis,
            default=[municipios_disponiveis[0]] if municipios_disponiveis else [],
            key="municipios_select",
            help="Selecione um ou mais municípios para comparar"
        )
        
        if not municipios_selecionados:
            st.warning("⚠️ Selecione pelo menos um município")
            st.stop()
    else:
        st.error("Nenhum município encontrado")
        st.stop()
    
    st.markdown("---")
    st.info(f"**{len(municipios_selecionados)} município(s) selecionado(s)**")
    
    # Opção de visualização
    if len(municipios_selecionados) > 1:
        modo_visualizacao = st.radio(
            "Modo de Visualização",
            ["Comparativo", "Individual"],
            index=0,
            help="Comparativo: todos em um gráfico | Individual: gráficos separados"
        )
    else:
        modo_visualizacao = "Individual"

    st.markdown("---")
    with st.expander("Fortaleza por bairros", expanded=False):
        bairros_disponiveis = obter_lista_bairros_fortaleza()

        if bairros_disponiveis:
            bairros_selecionados = st.multiselect(
                "Selecione os bairros",
                options=bairros_disponiveis,
                default=[bairros_disponiveis[0]],
                key="bairros_fortaleza_select",
                help="Análise separada de Fortaleza usando bairros como unidade de comparação"
            )

            if bairros_selecionados and len(bairros_selecionados) > 1:
                modo_visualizacao_fortaleza = st.radio(
                    "Modo de Visualização",
                    ["Comparativo", "Individual"],
                    index=0,
                    key="modo_fortaleza_select",
                    help="Comparativo: bairros em um gráfico | Individual: um bloco por bairro"
                )
            else:
                modo_visualizacao_fortaleza = "Individual"
        else:
            bairros_selecionados = []
            modo_visualizacao_fortaleza = "Individual"
            st.info("Gere os JSONs de Fortaleza para habilitar esta análise.")

# Carregar todos os dados
df_cmi = carregar_dados_por_tipo('CMI')
df_cmi_mil = carregar_dados_por_tipo('CMI_MIL')
df_nv = carregar_dados_por_tipo('NV')
df_ob = carregar_dados_por_tipo('OB')
df_fortaleza_cmi = carregar_dados_fortaleza('CMI')
df_fortaleza_cmi_mil = carregar_dados_fortaleza('CMI_MIL')
df_fortaleza_nv = carregar_dados_fortaleza('NV')
df_fortaleza_ob = carregar_dados_fortaleza('OB')

# Preparar dados para todos os municípios selecionados
dados_municipios = {}
for mun_sel in municipios_selecionados:
    nome_mun, uf_mun = mun_sel.rsplit(' - ', 1)
    dados_municipios[mun_sel] = {
        'cmi': df_cmi[(df_cmi['Municipio'] == nome_mun) & (df_cmi['UF'] == uf_mun)].sort_values('Ano'),
        'cmi_mil': df_cmi_mil[(df_cmi_mil['Municipio'] == nome_mun) & (df_cmi_mil['UF'] == uf_mun)].sort_values('Ano'),
        'nv': df_nv[(df_nv['Municipio'] == nome_mun) & (df_nv['UF'] == uf_mun)].sort_values('Ano'),
        'ob': df_ob[(df_ob['Municipio'] == nome_mun) & (df_ob['UF'] == uf_mun)].sort_values('Ano')
    }

# Verificar se há dados para pelo menos um município
tem_dados = any(
    not dados['cmi'].empty or not dados['cmi_mil'].empty or 
    not dados['nv'].empty or not dados['ob'].empty 
    for dados in dados_municipios.values()
)

if not tem_dados:
    st.error("Nenhum dado encontrado para os municípios selecionados")
    st.stop()

# Obter intervalo de anos disponível em todos os dados
anos_disponiveis = set()
for dados in dados_municipios.values():
    for df in [dados['cmi'], dados['cmi_mil'], dados['nv'], dados['ob']]:
        if not df.empty and 'Ano' in df.columns:
            anos_disponiveis.update(df['Ano'].unique())

if anos_disponiveis:
    ano_min = int(min(anos_disponiveis))
    ano_max = int(max(anos_disponiveis))
    
    # Adicionar filtro de anos na sidebar (após os municípios)
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 📅 Filtro de Período")
        
        intervalo_anos = st.slider(
            "Selecione o período de análise",
            min_value=ano_min,
            max_value=ano_max,
            value=(ano_min, ano_max),
            step=1,
            help="Arraste para ajustar o período inicial e final da análise"
        )
        
        ano_inicio, ano_fim = intervalo_anos
        st.caption(f"Período selecionado: **{ano_inicio}** a **{ano_fim}** ({ano_fim - ano_inicio + 1} anos)")
    
    # Filtrar dados de acordo com o período selecionado
    for mun_sel in dados_municipios:
        dados_municipios[mun_sel]['cmi'] = dados_municipios[mun_sel]['cmi'][
            (dados_municipios[mun_sel]['cmi']['Ano'] >= ano_inicio) & 
            (dados_municipios[mun_sel]['cmi']['Ano'] <= ano_fim)
        ]
        dados_municipios[mun_sel]['cmi_mil'] = dados_municipios[mun_sel]['cmi_mil'][
            (dados_municipios[mun_sel]['cmi_mil']['Ano'] >= ano_inicio) & 
            (dados_municipios[mun_sel]['cmi_mil']['Ano'] <= ano_fim)
        ]
        dados_municipios[mun_sel]['nv'] = dados_municipios[mun_sel]['nv'][
            (dados_municipios[mun_sel]['nv']['Ano'] >= ano_inicio) & 
            (dados_municipios[mun_sel]['nv']['Ano'] <= ano_fim)
        ]
        dados_municipios[mun_sel]['ob'] = dados_municipios[mun_sel]['ob'][
            (dados_municipios[mun_sel]['ob']['Ano'] >= ano_inicio) & 
            (dados_municipios[mun_sel]['ob']['Ano'] <= ano_fim)
        ]
else:
    ano_inicio = None
    ano_fim = None

if ano_inicio is not None and ano_fim is not None:
    if not df_fortaleza_cmi.empty:
        df_fortaleza_cmi = df_fortaleza_cmi[
            (df_fortaleza_cmi['Ano'] >= ano_inicio) &
            (df_fortaleza_cmi['Ano'] <= ano_fim)
        ]
    if not df_fortaleza_cmi_mil.empty:
        df_fortaleza_cmi_mil = df_fortaleza_cmi_mil[
            (df_fortaleza_cmi_mil['Ano'] >= ano_inicio) &
            (df_fortaleza_cmi_mil['Ano'] <= ano_fim)
        ]
    if not df_fortaleza_nv.empty:
        df_fortaleza_nv = df_fortaleza_nv[
            (df_fortaleza_nv['Ano'] >= ano_inicio) &
            (df_fortaleza_nv['Ano'] <= ano_fim)
        ]
    if not df_fortaleza_ob.empty:
        df_fortaleza_ob = df_fortaleza_ob[
            (df_fortaleza_ob['Ano'] >= ano_inicio) &
            (df_fortaleza_ob['Ano'] <= ano_fim)
        ]

if not tem_dados:
    st.error("Nenhum dado encontrado para os municípios selecionados")
    st.stop()

# ====================================================================================
# SEÇÃO 1: COEFICIENTE DE MORTALIDADE INFANTIL (CMI)
# ====================================================================================
st.markdown('<div class="section-header">Coeficiente de Mortalidade Infantil</div>', unsafe_allow_html=True)

if len(municipios_selecionados) > 1 and modo_visualizacao == "Comparativo":
    # Modo comparativo - todos os municípios em um gráfico
    
    # CMI-Mil PRIMEIRO - Largura total
    st.markdown("### CMI-Mil - Comparação entre Municípios")
    dados_cmi_mil_comp = {mun: dados['cmi_mil'] for mun, dados in dados_municipios.items() if not dados['cmi_mil'].empty}
    if dados_cmi_mil_comp:
        fig = criar_grafico_multiplos_municipios(dados_cmi_mil_comp, 'CMI-Mil', 'Comparação CMI-Mil')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Dados CMI-Mil não disponíveis")
    
    st.markdown("---")
    
    # SEGUNDA LINHA: CMI (esquerda) e Estatísticas (direita)
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### CMI - Comparação entre Municípios")
        dados_cmi_comp = {mun: dados['cmi'] for mun, dados in dados_municipios.items() if not dados['cmi'].empty}
        if dados_cmi_comp:
            fig = criar_grafico_multiplos_municipios(dados_cmi_comp, 'CMI', 'Comparação CMI')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Dados CMI não disponíveis")
    
    with col2:
        st.markdown("### Estatísticas Comparativas")
        
        # Preparar dados de estatísticas
        estatisticas_data = []
        for mun, dados in dados_municipios.items():
            if not dados['cmi'].empty:
                estatisticas_data.append({
                    'Município': mun,
                    'Indicador': 'CMI',
                    'Média': f"{dados['cmi']['Valor'].mean():.1f}",
                    'Mínimo': f"{dados['cmi']['Valor'].min():.1f}",
                    'Máximo': f"{dados['cmi']['Valor'].max():.1f}"
                })
            if not dados['cmi_mil'].empty:
                estatisticas_data.append({
                    'Município': mun,
                    'Indicador': 'CMI-Mil',
                    'Média': f"{dados['cmi_mil']['Valor'].mean():.1f}",
                    'Mínimo': f"{dados['cmi_mil']['Valor'].min():.1f}",
                    'Máximo': f"{dados['cmi_mil']['Valor'].max():.1f}"
                })
        
        if estatisticas_data:
            df_estatisticas = pd.DataFrame(estatisticas_data)
            st.dataframe(df_estatisticas, use_container_width=True, hide_index=True, height=400)
        else:
            st.info("Nenhuma estatística disponível")

else:
    # Modo individual - um município por vez ou apenas um selecionado
    for mun_sel in municipios_selecionados:
        nome_municipio, uf = mun_sel.rsplit(' - ', 1)
        dados_mun = dados_municipios[mun_sel]
        
        if len(municipios_selecionados) > 1:
            st.markdown(f"### {nome_municipio} - {uf}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if not dados_mun['cmi'].empty:
                st.plotly_chart(
                    criar_grafico_linha(dados_mun['cmi'], f"CMI - {nome_municipio}", '#e74c3c', 'CMI'),
                    use_container_width=True
                )
                
                col_a, col_b, col_c = st.columns(3)
                col_a.metric("Média", f"{dados_mun['cmi']['Valor'].mean():.1f}")
                col_b.metric("Mínimo", f"{dados_mun['cmi']['Valor'].min():.1f}")
                col_c.metric("Máximo", f"{dados_mun['cmi']['Valor'].max():.1f}")
            else:
                st.warning("Dados CMI não disponíveis")
        
        with col2:
            if not dados_mun['cmi_mil'].empty:
                st.plotly_chart(
                    criar_grafico_linha(dados_mun['cmi_mil'], f"CMI-Mil - {nome_municipio}", '#3498db', 'CMI-Mil'),
                    use_container_width=True
                )
                
                col_a, col_b, col_c = st.columns(3)
                col_a.metric("Média", f"{dados_mun['cmi_mil']['Valor'].mean():.1f}")
                col_b.metric("Mínimo", f"{dados_mun['cmi_mil']['Valor'].min():.1f}")
                col_c.metric("Máximo", f"{dados_mun['cmi_mil']['Valor'].max():.1f}")
            else:
                st.warning("Dados CMI-Mil não disponíveis")
        
        if len(municipios_selecionados) > 1:
            st.markdown("---")

# Comparação CMI vs CMI-MIL
st.markdown("---")
st.markdown("### Comparação CMI vs CMI-Mil")

if len(municipios_selecionados) > 1 and modo_visualizacao == "Comparativo":
    # Mostrar comparações lado a lado para cada município
    for mun_sel in municipios_selecionados:
        nome_municipio, uf = mun_sel.rsplit(' - ', 1)
        dados_mun = dados_municipios[mun_sel]
        
        if not dados_mun['cmi'].empty and not dados_mun['cmi_mil'].empty:
            st.markdown(f"#### {nome_municipio} - {uf}")
            st.plotly_chart(
                criar_grafico_comparacao(dados_mun['cmi'], dados_mun['cmi_mil'], 'CMI', 'CMI-Mil', 
                                        f'CMI vs CMI-Mil - {nome_municipio}'),
                use_container_width=True
            )
else:
    # Modo individual
    for mun_sel in municipios_selecionados:
        nome_municipio, uf = mun_sel.rsplit(' - ', 1)
        dados_mun = dados_municipios[mun_sel]
        
        if not dados_mun['cmi'].empty and not dados_mun['cmi_mil'].empty:
            if len(municipios_selecionados) > 1:
                st.markdown(f"#### {nome_municipio} - {uf}")
            
            st.plotly_chart(
                criar_grafico_comparacao(dados_mun['cmi'], dados_mun['cmi_mil'], 'CMI', 'CMI-Mil', 
                                        f'Comparação CMI vs CMI-Mil - {nome_municipio}'),
                use_container_width=True
            )

st.markdown("""
<div class="explanation-box">
<b>Sobre esta comparação:</b><br>
• <b>CMI</b>: Métrica tradicional de mortalidade infantil, pode apresentar imprecisões devido à metodologia de cálculo<br>
• <b>CMI-Mil</b>: Indicador baseado em dados factuais e melhor metodologia, gerando resultados mais fiéis à realidade<br>
• Esta visualização permite comparar as duas métricas ao longo do tempo e identificar discrepâncias
</div>
""", unsafe_allow_html=True)

# ====================================================================================
# SEÇÃO 3: FORTALEZA POR BAIRROS
# ====================================================================================
if 'bairros_selecionados' in locals() and bairros_selecionados:
    st.markdown('<div class="section-header">Fortaleza por Bairros</div>', unsafe_allow_html=True)

    dados_bairros = {}
    for bairro in bairros_selecionados:
        dados_bairros[bairro] = {
            'cmi': df_fortaleza_cmi[df_fortaleza_cmi['Bairro'] == bairro].sort_values('Ano') if not df_fortaleza_cmi.empty else pd.DataFrame(),
            'cmi_mil': df_fortaleza_cmi_mil[df_fortaleza_cmi_mil['Bairro'] == bairro].sort_values('Ano') if not df_fortaleza_cmi_mil.empty else pd.DataFrame(),
            'nv': df_fortaleza_nv[df_fortaleza_nv['Bairro'] == bairro].sort_values('Ano') if not df_fortaleza_nv.empty else pd.DataFrame(),
            'ob': df_fortaleza_ob[df_fortaleza_ob['Bairro'] == bairro].sort_values('Ano') if not df_fortaleza_ob.empty else pd.DataFrame(),
        }

    tem_dados_fortaleza = any(
        not dados['cmi'].empty or not dados['cmi_mil'].empty or
        not dados['nv'].empty or not dados['ob'].empty
        for dados in dados_bairros.values()
    )

    if not tem_dados_fortaleza:
        st.warning("Nenhum dado de Fortaleza encontrado para os bairros selecionados")
    elif len(bairros_selecionados) > 1 and modo_visualizacao_fortaleza == "Comparativo":
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### CMI-Mil - Comparação entre Bairros")
            dados_cmi_mil_comp = {bairro: dados['cmi_mil'] for bairro, dados in dados_bairros.items() if not dados['cmi_mil'].empty}
            if dados_cmi_mil_comp:
                fig = criar_grafico_multiplos_municipios(dados_cmi_mil_comp, 'CMI-Mil', 'Fortaleza - Comparação CMI-Mil por Bairro')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Dados CMI-Mil não disponíveis para os bairros selecionados")

        with col2:
            st.markdown("### CMI - Comparação entre Bairros")
            dados_cmi_comp = {bairro: dados['cmi'] for bairro, dados in dados_bairros.items() if not dados['cmi'].empty}
            if dados_cmi_comp:
                fig = criar_grafico_multiplos_municipios(dados_cmi_comp, 'CMI', 'Fortaleza - Comparação CMI por Bairro')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Dados CMI não disponíveis para os bairros selecionados")

        # Gráfico combinado: cada bairro tem CMI (linha sólida) e CMI-Mil (linha tracejada) com mesma cor
        st.markdown("### CMI vs CMI-Mil - Comparação direta por Bairro")
        fig_comb = go.Figure()
        cores = px.colors.qualitative.Set2 + px.colors.qualitative.Pastel
        for idx, bairro in enumerate(bairros_selecionados):
            cor = cores[idx % len(cores)]
            df_cmi_b = dados_bairros[bairro]['cmi']
            df_mil_b = dados_bairros[bairro]['cmi_mil']

            if not df_cmi_b.empty:
                fig_comb.add_trace(go.Scatter(
                    x=df_cmi_b['Ano'], y=df_cmi_b['Valor'],
                    mode='lines+markers', name=f"{bairro} - CMI",
                    line=dict(color=cor, width=2), marker=dict(size=6)
                ))

            if not df_mil_b.empty:
                fig_comb.add_trace(go.Scatter(
                    x=df_mil_b['Ano'], y=df_mil_b['Valor'],
                    mode='lines+markers', name=f"{bairro} - CMI-Mil",
                    line=dict(color=cor, width=2, dash='dash'), marker=dict(size=6)
                ))

        fig_comb.update_layout(
            title='Fortaleza: CMI vs CMI-Mil (bairros selecionados)',
            xaxis_title='Ano', yaxis_title='Valor', hovermode='x unified',
            template='plotly_white', height=550
        )

        if fig_comb.data:
            st.plotly_chart(fig_comb, use_container_width=True)

        st.markdown("### Resumo comparativo dos bairros")
        resumo_bairros = []
        for bairro, dados in dados_bairros.items():
            cmi_media = dados['cmi']['Valor'].mean() if not dados['cmi'].empty else np.nan
            cmi_mil_media = dados['cmi_mil']['Valor'].mean() if not dados['cmi_mil'].empty else np.nan
            resumo_bairros.append({
                'Bairro': bairro,
                'Óbitos': int(dados['ob']['Valor'].sum()) if not dados['ob'].empty else 0,
                'Nascidos Vivos': int(dados['nv']['Valor'].sum()) if not dados['nv'].empty else 0,
                'Média CMI': f"{cmi_media:.1f}" if pd.notna(cmi_media) else '-',
                'Média CMI-Mil': f"{cmi_mil_media:.1f}" if pd.notna(cmi_mil_media) else '-',
                'Dif. Média': f"{(cmi_media - cmi_mil_media):.1f}" if pd.notna(cmi_media) and pd.notna(cmi_mil_media) else '-'
            })

        st.dataframe(pd.DataFrame(resumo_bairros), use_container_width=True, hide_index=True)
    else:
        for bairro, dados in dados_bairros.items():
            if len(bairros_selecionados) > 1:
                st.markdown(f"#### {bairro}")

            col1, col2 = st.columns(2)

            with col1:
                if not dados['cmi'].empty:
                    st.plotly_chart(
                        criar_grafico_linha(dados['cmi'], f"CMI - {bairro}", '#e74c3c', 'CMI'),
                        use_container_width=True
                    )
                else:
                    st.warning(f"Dados CMI não disponíveis para {bairro}")

            with col2:
                if not dados['cmi_mil'].empty:
                    st.plotly_chart(
                        criar_grafico_linha(dados['cmi_mil'], f"CMI-Mil - {bairro}", '#3498db', 'CMI-Mil'),
                        use_container_width=True
                    )
                else:
                    st.warning(f"Dados CMI-Mil não disponíveis para {bairro}")

            if not dados['cmi'].empty and not dados['cmi_mil'].empty:
                st.plotly_chart(
                    criar_grafico_comparacao(dados['cmi'], dados['cmi_mil'], 'CMI', 'CMI-Mil', f'Fortaleza - CMI vs CMI-Mil - {bairro}'),
                    use_container_width=True
                )

            tabela_bairro = None
            if not dados['nv'].empty:
                tabela_bairro = dados['nv'][['Ano', 'Valor']].rename(columns={'Valor': 'Nascidos Vivos'})
            if not dados['ob'].empty:
                df_obitos = dados['ob'][['Ano', 'Valor']].rename(columns={'Valor': 'Óbitos'})
                tabela_bairro = df_obitos if tabela_bairro is None else pd.merge(tabela_bairro, df_obitos, on='Ano', how='outer')
            if not dados['cmi'].empty:
                df_cmi_bairro = dados['cmi'][['Ano', 'Valor']].rename(columns={'Valor': 'CMI'})
                tabela_bairro = df_cmi_bairro if tabela_bairro is None else pd.merge(tabela_bairro, df_cmi_bairro, on='Ano', how='outer')
            if not dados['cmi_mil'].empty:
                df_cmi_mil_bairro = dados['cmi_mil'][['Ano', 'Valor']].rename(columns={'Valor': 'CMI-Mil'})
                tabela_bairro = df_cmi_mil_bairro if tabela_bairro is None else pd.merge(tabela_bairro, df_cmi_mil_bairro, on='Ano', how='outer')

            if tabela_bairro is not None:
                st.markdown("##### Tabela de comparação anual")
                st.dataframe(tabela_bairro.sort_values('Ano'), use_container_width=True, hide_index=True)

            if len(bairros_selecionados) > 1:
                st.markdown("---")

# ====================================================================================
# SEÇÃO 2: NASCIDOS VIVOS E ÓBITOS
# ====================================================================================
st.markdown('<div class="section-header">Nascidos Vivos e Óbitos Infantis</div>', unsafe_allow_html=True)

if len(municipios_selecionados) > 1 and modo_visualizacao == "Comparativo":
    # Modo comparativo
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Nascidos Vivos - Comparação")
        dados_nv_comp = {mun: dados['nv'] for mun, dados in dados_municipios.items() if not dados['nv'].empty}
        if dados_nv_comp:
            fig = criar_grafico_multiplos_municipios(dados_nv_comp, 'Nascidos Vivos', 'Comparação de Nascidos Vivos')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Dados de Nascidos Vivos não disponíveis")
    
    with col2:
        st.markdown("### Óbitos Infantis - Comparação")
        dados_ob_comp = {mun: dados['ob'] for mun, dados in dados_municipios.items() if not dados['ob'].empty}
        if dados_ob_comp:
            fig = criar_grafico_multiplos_municipios(dados_ob_comp, 'Óbitos', 'Comparação de Óbitos Infantis')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Dados de Óbitos não disponíveis")
    
    # Tabela comparativa
    st.markdown("### Estatísticas Comparativas")
    estatisticas_nv_ob = []
    for mun, dados in dados_municipios.items():
        if not dados['nv'].empty:
            estatisticas_nv_ob.append({
                'Município': mun,
                'Indicador': 'Nascidos Vivos',
                'Total': f"{dados['nv']['Valor'].sum():,}",
                'Média Anual': f"{dados['nv']['Valor'].mean():.0f}",
                'Mín': f"{dados['nv']['Valor'].min()}",
                'Máx': f"{dados['nv']['Valor'].max()}"
            })
        if not dados['ob'].empty:
            estatisticas_nv_ob.append({
                'Município': mun,
                'Indicador': 'Óbitos Infantis',
                'Total': f"{dados['ob']['Valor'].sum():,}",
                'Média Anual': f"{dados['ob']['Valor'].mean():.0f}",
                'Mín': f"{dados['ob']['Valor'].min()}",
                'Máx': f"{dados['ob']['Valor'].max()}"
            })
    
    if estatisticas_nv_ob:
        df_stats = pd.DataFrame(estatisticas_nv_ob)
        st.dataframe(df_stats, use_container_width=True, hide_index=True)

else:
    # Modo individual
    for mun_sel in municipios_selecionados:
        nome_municipio, uf = mun_sel.rsplit(' - ', 1)
        dados_mun = dados_municipios[mun_sel]
        
        if len(municipios_selecionados) > 1:
            st.markdown(f"### {nome_municipio} - {uf}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Nascidos Vivos")
            if not dados_mun['nv'].empty:
                st.plotly_chart(
                    criar_grafico_linha(dados_mun['nv'], f"Nascidos Vivos - {nome_municipio}", '#2ecc71', 'Nascidos Vivos'),
                    use_container_width=True
                )
                
                col_a, col_b, col_c, col_d = st.columns(4)
                total_nv = dados_mun['nv']['Valor'].sum()
                media_nv = dados_mun['nv']['Valor'].mean()
                min_nv = dados_mun['nv']['Valor'].min()
                max_nv = dados_mun['nv']['Valor'].max()
                
                col_a.metric("Total", f"{total_nv:,}")
                col_b.metric("Média Anual", f"{media_nv:.0f}")
                col_c.metric("Mínimo", f"{min_nv}")
                col_d.metric("Máximo", f"{max_nv}")
            else:
                st.warning("Dados de Nascidos Vivos não disponíveis")
        
        with col2:
            st.markdown("#### Óbitos Infantis")
            if not dados_mun['ob'].empty:
                st.plotly_chart(
                    criar_grafico_linha(dados_mun['ob'], f"Óbitos Infantis - {nome_municipio}", '#e67e22', 'Óbitos'),
                    use_container_width=True
                )
                
                col_a, col_b, col_c, col_d = st.columns(4)
                total_ob = dados_mun['ob']['Valor'].sum()
                media_ob = dados_mun['ob']['Valor'].mean()
                min_ob = dados_mun['ob']['Valor'].min()
                max_ob = dados_mun['ob']['Valor'].max()
                
                col_a.metric("Total", f"{total_ob:,}")
                col_b.metric("Média Anual", f"{media_ob:.0f}")
                col_c.metric("Mínimo", f"{min_ob}")
                col_d.metric("Máximo", f"{max_ob}")
            else:
                st.warning("Dados de Óbitos não disponíveis")
        
        if len(municipios_selecionados) > 1:
            st.markdown("---")

# ====================================================================================
# SEÇÃO 3: MÉTRICAS COMPARATIVAS
# ====================================================================================
st.markdown('<div class="section-header">Métricas Comparativas</div>', unsafe_allow_html=True)

# Criar abas para cada métrica
tab1, tab2, tab3 = st.tabs([
    "Diferença Absoluta",
    "Correlação",
    "Análise de Períodos"
])

# TAB 1: Diferença Absoluta CMI vs CMI-Mil
with tab1:
    st.markdown("### Diferença Absoluta: CMI vs CMI-Mil")
    
    st.markdown("""
    <div class="explanation-box">
    <b>Como interpretar:</b><br>
    • <b style="color: green;">Barras verdes</b>: CMI é maior que CMI-Mil (possível superestimação do CMI)<br>
    • <b style="color: red;">Barras vermelhas</b>: CMI é menor que CMI-Mil (possível subestimação do CMI)<br>
    • Quanto maior a barra, maior a discrepância entre as duas métricas
    </div>
    """, unsafe_allow_html=True)
    
    for mun_sel in municipios_selecionados:
        nome_municipio, uf = mun_sel.rsplit(' - ', 1)
        dados_mun = dados_municipios[mun_sel]
        
        if not dados_mun['cmi'].empty and not dados_mun['cmi_mil'].empty:
            if len(municipios_selecionados) > 1:
                st.markdown(f"#### {nome_municipio} - {uf}")
            
            # Merge dos dados
            df_merged = pd.merge(
                dados_mun['cmi'][['Ano', 'Valor']],
                dados_mun['cmi_mil'][['Ano', 'Valor']],
                on='Ano',
                suffixes=('_CMI', '_CMI_MIL')
            )
            df_merged['Diferenca'] = df_merged['Valor_CMI'] - df_merged['Valor_CMI_MIL']
            
            # Gráfico de diferença
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df_merged['Ano'],
                y=df_merged['Diferenca'],
                marker_color=['green' if x >= 0 else 'red' for x in df_merged['Diferenca']],
                name='Diferença (CMI - CMI-Mil)'
            ))
            fig.update_layout(
                title=f'Diferença Absoluta entre CMI e CMI-Mil - {nome_municipio}',
                xaxis_title='Ano',
                yaxis_title='Diferença',
                template='plotly_white',
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Estatísticas
            col1, col2, col3 = st.columns(3)
            col1.metric("Média da Diferença", f"{df_merged['Diferenca'].mean():.1f}")
            col2.metric("Maior Diferença", f"{df_merged['Diferenca'].max():.1f}")
            col3.metric("Menor Diferença", f"{df_merged['Diferenca'].min():.1f}")
            
            if len(municipios_selecionados) > 1:
                st.markdown("---")

# TAB 2: Correlação
with tab2:
    st.markdown("### Correlação entre CMI e CMI-Mil")
    
    st.markdown("""
    <div class="explanation-box">
    <b>O que este gráfico mostra:</b><br>
    • Cada ponto representa um ano de dados<br>
    • Se os pontos estiverem próximos da linha de tendência (vermelha), indica alta correlação<br>
    • Correlação > 0.7 = Alta similaridade entre as métricas<br>
    • Correlação entre 0.4 e 0.7 = Similaridade moderada<br>
    • Correlação < 0.4 = Baixa similaridade (maior discrepância entre as métricas)
    </div>
    """, unsafe_allow_html=True)
    
    for mun_sel in municipios_selecionados:
        nome_municipio, uf = mun_sel.rsplit(' - ', 1)
        dados_mun = dados_municipios[mun_sel]
        
        if not dados_mun['cmi'].empty and not dados_mun['cmi_mil'].empty:
            if len(municipios_selecionados) > 1:
                st.markdown(f"#### {nome_municipio} - {uf}")
            
            df_merged = pd.merge(
                dados_mun['cmi'][['Ano', 'Valor']],
                dados_mun['cmi_mil'][['Ano', 'Valor']],
                on='Ano',
                suffixes=('_CMI', '_CMI_MIL')
            )
            
            correlacao = df_merged['Valor_CMI'].corr(df_merged['Valor_CMI_MIL'])
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.metric(
                    "Correlação CMI ↔ CMI-Mil",
                    f"{correlacao:.3f}",
                    delta="Alta correlação" if abs(correlacao) > 0.7 else "Correlação moderada"
                )
                
                if abs(correlacao) > 0.7:
                    interpretacao = "As duas métricas apresentam comportamento similar ao longo do tempo."
                elif abs(correlacao) > 0.4:
                    interpretacao = "As métricas mostram alguma similaridade, mas com discrepâncias notáveis."
                else:
                    interpretacao = "As métricas divergem significativamente, indicando diferenças metodológicas importantes."
                
                st.markdown(f"""
                <div class="info-box">
                <b>Interpretação:</b><br>
                {interpretacao}
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                # Scatter plot
                fig = px.scatter(
                    df_merged,
                    x='Valor_CMI',
                    y='Valor_CMI_MIL',
                    labels={'Valor_CMI': 'CMI', 'Valor_CMI_MIL': 'CMI-Mil'},
                    title=f'Correlação: CMI vs CMI-Mil - {nome_municipio}'
                )
                
                # Adicionar linha de tendência manual
                if len(df_merged) > 1:
                    z = np.polyfit(df_merged['Valor_CMI'], df_merged['Valor_CMI_MIL'], 1)
                    p = np.poly1d(z)
                    x_line = np.linspace(df_merged['Valor_CMI'].min(), df_merged['Valor_CMI'].max(), 100)
                    fig.add_trace(go.Scatter(
                        x=x_line, 
                        y=p(x_line), 
                        mode='lines', 
                        name='Tendência',
                        line=dict(color='red', dash='dash')
                    ))
                
                fig.update_layout(height=350)
                st.plotly_chart(fig, use_container_width=True)
            
            if len(municipios_selecionados) > 1:
                st.markdown("---")

# TAB 3: Análise de Períodos
with tab3:
    st.markdown("### Análise de Períodos: Nascidos Vivos e Óbitos")
    
    st.markdown("""
    <div class="explanation-box">
    <b>Esta análise divide os dados em dois períodos iguais para identificar:</b><br>
    • Mudanças na taxa de natalidade ao longo do tempo<br>
    • Variações na mortalidade infantil<br>
    • Anos com melhores e piores indicadores (menor óbito = melhor ano)
    </div>
    """, unsafe_allow_html=True)
    
    for mun_sel in municipios_selecionados:
        nome_municipio, uf = mun_sel.rsplit(' - ', 1)
        dados_mun = dados_municipios[mun_sel]
        
        if len(municipios_selecionados) > 1:
            st.markdown(f"#### {nome_municipio} - {uf}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### Nascidos Vivos")
            if not dados_mun['nv'].empty and len(dados_mun['nv']) > 1:
                # Dividir em períodos
                meio = len(dados_mun['nv']) // 2
                periodo1 = dados_mun['nv'].iloc[:meio]
                periodo2 = dados_mun['nv'].iloc[meio:]
                
                media_p1 = periodo1['Valor'].mean()
                media_p2 = periodo2['Valor'].mean()
                variacao = ((media_p2 - media_p1) / media_p1) * 100
                
                st.metric(
                    f"Variação ({periodo1['Ano'].min()}-{periodo1['Ano'].max()} → {periodo2['Ano'].min()}-{periodo2['Ano'].max()})",
                    f"{variacao:+.1f}%",
                    delta=f"{media_p2 - media_p1:+.0f} nascimentos/ano"
                )
                
                # Melhor e pior ano
                melhor_ano = dados_mun['nv'].loc[dados_mun['nv']['Valor'].idxmax()]
                pior_ano = dados_mun['nv'].loc[dados_mun['nv']['Valor'].idxmin()]
                
                st.info(f"**Maior natalidade:** {melhor_ano['Ano']} ({melhor_ano['Valor']} nascimentos)")
                st.warning(f"**Menor natalidade:** {pior_ano['Ano']} ({pior_ano['Valor']} nascimentos)")
            else:
                st.warning("Dados insuficientes")
        
        with col2:
            st.markdown("##### Óbitos Infantis")
            if not dados_mun['ob'].empty and len(dados_mun['ob']) > 1:
                # Dividir em períodos
                meio = len(dados_mun['ob']) // 2
                periodo1 = dados_mun['ob'].iloc[:meio]
                periodo2 = dados_mun['ob'].iloc[meio:]
                
                media_p1 = periodo1['Valor'].mean()
                media_p2 = periodo2['Valor'].mean()
                variacao = ((media_p2 - media_p1) / media_p1) * 100 if media_p1 > 0 else 0
                
                st.metric(
                    f"Variação ({periodo1['Ano'].min()}-{periodo1['Ano'].max()} → {periodo2['Ano'].min()}-{periodo2['Ano'].max()})",
                    f"{variacao:+.1f}%",
                    delta=f"{media_p2 - media_p1:+.1f} óbitos/ano"
                )
                
                # Melhor (menor) e pior (maior) ano
                melhor_ano = dados_mun['ob'].loc[dados_mun['ob']['Valor'].idxmin()]
                pior_ano = dados_mun['ob'].loc[dados_mun['ob']['Valor'].idxmax()]
                
                st.success(f"**Melhor ano (menos óbitos):** {melhor_ano['Ano']} ({melhor_ano['Valor']} óbitos)")
                st.error(f"**Pior ano (mais óbitos):** {pior_ano['Ano']} ({pior_ano['Valor']} óbitos)")
            else:
                st.warning("Dados insuficientes")
        
        if len(municipios_selecionados) > 1:
            st.markdown("---")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #7f8c8d; padding: 2rem 0;'>
    <p><b>Dashboard de Análise de Saúde Municipal</b></p>
    <p>Dados: CMI, CMI-Mil, Nascidos Vivos e Óbitos | 1996-2024</p>
</div>
""", unsafe_allow_html=True)
