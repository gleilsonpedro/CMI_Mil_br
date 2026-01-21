"""
Dashboard Streamlit para visualização de dados de Saúde
Contém: CMI-Mil, CMI + Análise Original de Nascidos Vivos e Óbitos
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from pathlib import Path
import re

# Configuração da página
st.set_page_config(
    page_title="Dashboard Saúde - Análises Completas",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para melhorar UX
st.markdown("""
    <style>
    /* Cor de fundo do sidebar - azul escuro para combinar com tema dark */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e3a8a 0%, #1e293b 100%) !important;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background: linear-gradient(180deg, #1e3a8a 0%, #1e293b 100%) !important;
    }
    
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e3a8a 0%, #1e293b 100%) !important;
    }
    
    /* Textos claros na sidebar para contraste com fundo escuro */
    [data-testid="stSidebar"] label {
        color: #e0f2fe !important;
        font-weight: 500;
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: #e0f2fe !important;
    }
    
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #ffffff !important;
    }
    
    /* Widgets na sidebar */
    [data-testid="stSidebar"] .stSelectbox > div > div,
    [data-testid="stSidebar"] .stMultiSelect > div > div {
        background-color: #334155 !important;
        color: #e0f2fe !important;
    }
    
    [data-testid="stSidebar"] input {
        background-color: #334155 !important;
        color: #e0f2fe !important;
    }
    
    /* Separadores na sidebar */
    [data-testid="stSidebar"] hr {
        border-color: #475569 !important;
    }
    
    /* Estilo dos títulos principais */
    h1 {
        color: #3b82f6;
        font-weight: 700;
    }
    
    h2, h3 {
        color: #60a5fa;
    }
    
    /* Estilo das métricas */
    [data-testid="stMetricValue"] {
        font-size: 28px;
        font-weight: 600;
        color: #10b981;
    }
    
    /* Botões */
    .stButton>button {
        background-color: #3b82f6;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }
    
    .stButton>button:hover {
        background-color: #2563eb;
        border: none;
    }
    
    /* Dataframes */
    [data-testid="stDataFrame"] {
        border-radius: 8px;
    }
    
    /* Cards de métricas */
    div[data-testid="metric-container"] {
        background-color: rgba(30, 41, 59, 0.5);
        border: 1px solid #334155;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.3);
    }
    </style>
""", unsafe_allow_html=True)

# Caminhos
BASE_DIR = Path(__file__).parent
DIR_NV = BASE_DIR / 'data' / 'output' / 'nascidos_vivos'
DIR_OB = BASE_DIR / 'data' / 'output' / 'obitos'
DIR_CMI_PURO = BASE_DIR / 'data' / 'output' / 'CMI_puro'
DIR_CMI_MIL = BASE_DIR / 'data' / 'output' / 'CMI_MIL'

# Paleta de cores personalizada
CORES = {
    'primaria': '#3b82f6',      # Azul moderno
    'secundaria': '#10b981',    # Verde
    'terciaria': '#f59e0b',     # Laranja
    'quaternaria': '#8b5cf6',   # Roxo
    'destaque': '#ef4444',      # Vermelho
    'sucesso': '#059669',       # Verde escuro
}

# Esquema de cores vibrantes para gráficos - otimizado para tema escuro
COLOR_SCALE = [
    '#0ea5e9',  # Azul cyan vibrante
    '#22c55e',  # Verde limão vibrante
    '#f59e0b',  # Laranja âmbar
    '#a78bfa',  # Roxo lavanda
    '#ef4444',  # Vermelho coral
    '#14b8a6',  # Turquesa
    '#f97316',  # Laranja intenso
    '#ec4899',  # Rosa pink
    '#06b6d4',  # Cyan claro
    '#84cc16',  # Verde lima
    '#eab308',  # Amarelo vibrante
    '#d946ef',  # Magenta
]

# Função auxiliar para limpar nomes de municípios
def limpar_nome_municipio(nome):
    """
    Remove códigos numéricos, 'NOTAS:', estado e outros textos indesejados do nome do município
    """
    if pd.isna(nome):
        return nome
    
    # Remove código numérico no início (ex: "230010 ABAIARA" -> "ABAIARA")
    nome_limpo = re.sub(r'^\d+\s*', '', str(nome))
    
    # Remove "NOTAS:" e variações
    nome_limpo = re.sub(r'(?i)notas?:?\s*', '', nome_limpo)
    
    # Remove "utilizados simultaneamente" e variações
    nome_limpo = re.sub(r'(?i)utilizados?\s+simultaneamente', '', nome_limpo)
    
    # Remove siglas de estados no final (ex: " - CE", " CE")
    nome_limpo = re.sub(r'\s*-?\s*[A-Z]{2}\s*$', '', nome_limpo)
    
    # Remove "MUNICIPIO IGNORADO"
    if 'IGNORADO' in nome_limpo.upper():
        return None
    
    # Remove espaços extras
    nome_limpo = ' '.join(nome_limpo.split())
    
    return nome_limpo.strip() if nome_limpo.strip() else None

# Cache dos dados
@st.cache_data
def carregar_dados_uf(uf, tipo):
    """
    Carrega dados de uma UF específica
    """
    if tipo == 'CMI-Mil':
        diretorio = DIR_CMI_MIL
    elif tipo == 'CMI':
        diretorio = DIR_CMI_PURO
    elif tipo == 'NV':
        diretorio = DIR_NV
    else:  # OB
        diretorio = DIR_OB
    
    arquivo = diretorio / f"{uf}.json"
    
    if not arquivo.exists():
        return None
    
    with open(arquivo, 'r', encoding='utf-8') as f:
        dados = json.load(f)
    
    df = pd.DataFrame(dados)
    
    # Limpa nomes de municípios
    if 'Municipio' in df.columns:
        df['Municipio'] = df['Municipio'].apply(limpar_nome_municipio)
        # Remove linhas com municípios inválidos
        df = df.dropna(subset=['Municipio'])
    
    return df

@st.cache_data
def listar_ufs_disponiveis():
    """
    Lista todas as UFs que têm dados disponíveis
    """
    ufs = []
    for arquivo in DIR_OB.glob("*.json"):
        uf = arquivo.stem
        ufs.append(uf)
    return sorted(ufs)

@st.cache_data
def carregar_dados_multiplas_ufs(ufs, tipo):
    """
    Carrega e concatena dados de múltiplas UFs
    """
    dfs = []
    for uf in ufs:
        df = carregar_dados_uf(uf, tipo)
        if df is not None:
            dfs.append(df)
    
    if dfs:
        return pd.concat(dfs, ignore_index=True)
    return None

def calcular_metricas(df, ano_atual, ano_anterior):
    """
    Calcula métricas e variação entre anos
    """
    if df is None or len(df) == 0:
        return None, None, None
    
    total_atual = df[df['Ano'] == ano_atual]['Valor'].sum()
    total_anterior = df[df['Ano'] == ano_anterior]['Valor'].sum()
    
    if total_anterior > 0:
        variacao = ((total_atual - total_anterior) / total_anterior) * 100
    else:
        variacao = 0
    
    return total_atual, total_anterior, variacao

# ===== INTERFACE PRINCIPAL =====
st.title("Dashboard de Saúde Pública - Análises Completas")
st.markdown("### CMI-Mil | CMI | Nascidos Vivos | Óbitos")

# Sidebar
st.sidebar.header("Filtros")

# Modo de visualização
modo_visualizacao = st.sidebar.radio(
    "Escolha o Tipo de Análise",
    ["CMI-Mil", "CMI", "Nascidos Vivos e Óbitos"],
    index=0
)

# Verifica se há dados disponíveis
ufs_disponiveis = listar_ufs_disponiveis()

if not ufs_disponiveis:
    st.error("Nenhum dado encontrado! Execute primeiro o script converter_dados.py")
    st.stop()

# ====================================================================
# SEÇÃO 1: CMI-MIL e CMI
# ====================================================================

if modo_visualizacao in ["CMI-Mil", "CMI"]:
    st.sidebar.markdown("---")
    
    tipo_cod = modo_visualizacao
    
    # Seleciona múltiplos estados
    ufs_selecionadas = st.sidebar.multiselect(
        "Selecione os Estados para Comparar",
        ufs_disponiveis,
        default=ufs_disponiveis[:3] if len(ufs_disponiveis) >= 3 else ufs_disponiveis
    )
    
    if not ufs_selecionadas:
        st.warning("Selecione pelo menos um estado para comparar")
        st.stop()
    
    # Carrega dados
    if modo_visualizacao == "CMI":
        df_cmi_mil = carregar_dados_multiplas_ufs(ufs_selecionadas, 'CMI-Mil')
        df_cmi = carregar_dados_multiplas_ufs(ufs_selecionadas, 'CMI')
        
        if df_cmi_mil is None or len(df_cmi_mil) == 0 or df_cmi is None or len(df_cmi) == 0:
            st.error("Não há dados CMI ou CMI-Mil para os estados selecionados")
            st.stop()
        
        # Filtro de Anos
        anos_mil = set(df_cmi_mil['Ano'].unique())
        anos_cmi = set(df_cmi['Ano'].unique())
        anos_disponiveis = sorted(list(anos_mil & anos_cmi))
        
        if not anos_disponiveis:
            st.error("Nenhum ano em comum entre as duas bases de dados")
            st.stop()
        
        ano_min = int(min(anos_disponiveis))
        ano_max = int(max(anos_disponiveis))
        
        anos_selecionados = st.sidebar.slider(
            "Período",
            ano_min,
            ano_max,
            (ano_min, ano_max)
        )
        
        df_cmi_mil_filtrado = df_cmi_mil[
            (df_cmi_mil['Ano'] >= anos_selecionados[0]) & 
            (df_cmi_mil['Ano'] <= anos_selecionados[1])
        ]
        
        df_cmi_filtrado = df_cmi[
            (df_cmi['Ano'] >= anos_selecionados[0]) & 
            (df_cmi['Ano'] <= anos_selecionados[1])
        ]
        
        # ===== VISUALIZAÇÃO CMI =====
        st.title("Comparação CMI vs CMI-Mil")
        st.markdown(f"### Análise Comparativa - {len(ufs_selecionadas)} Estados")
        
        # Métricas
        col1, col2, col3, col4 = st.columns(4)
        
        media_cmi_mil = df_cmi_mil_filtrado['Valor'].mean()
        media_cmi = df_cmi_filtrado['Valor'].mean()
        diferenca = media_cmi_mil - media_cmi
        perc_diferenca = (diferenca / media_cmi * 100) if media_cmi > 0 else 0
        
        with col1:
            st.metric("Média CMI-Mil", f"{media_cmi_mil:.2f}")
        with col2:
            st.metric("Média CMI", f"{media_cmi:.2f}")
        with col3:
            st.metric("Diferença Absoluta", f"{diferenca:.2f}")
        with col4:
            st.metric("Diferença (%)", f"{perc_diferenca:+.2f}%")
        
        # Gráfico temporal - MÉDIA
        st.markdown("---")
        st.subheader("Evolução Temporal: CMI vs CMI-Mil (Média dos Estados Selecionados)")
        
        df_cmi_mil_ano = df_cmi_mil_filtrado.groupby('Ano')['Valor'].mean().reset_index()
        df_cmi_ano = df_cmi_filtrado.groupby('Ano')['Valor'].mean().reset_index()
        
        df_cmi_mil_ano['Indicador'] = 'CMI-Mil (Média)'
        df_cmi_ano['Indicador'] = 'CMI (Média)'
        df_combined = pd.concat([df_cmi_mil_ano, df_cmi_ano])
        
        fig_comp = px.line(
            df_combined,
            x='Ano',
            y='Valor',
            color='Indicador',
            title=f"Média - Comparação ({anos_selecionados[0]}-{anos_selecionados[1]})",
            markers=True,
            color_discrete_map={
                'CMI-Mil (Média)': '#f59e0b',  # Laranja
                'CMI (Média)': '#0ea5e9'  # Azul
            }
        )
        fig_comp.update_layout(hovermode='x unified', height=500)
        st.plotly_chart(fig_comp, use_container_width=True)
        
        # Gráfico temporal - TOTAL
        st.markdown("---")
        st.subheader("Evolução Temporal: CMI vs CMI-Mil (Total Agregado dos Estados Selecionados)")
        
        df_cmi_mil_ano_total = df_cmi_mil_filtrado.groupby('Ano')['Valor'].sum().reset_index()
        df_cmi_ano_total = df_cmi_filtrado.groupby('Ano')['Valor'].sum().reset_index()
        
        df_cmi_mil_ano_total['Indicador'] = 'CMI-Mil (Total)'
        df_cmi_ano_total['Indicador'] = 'CMI (Total)'
        df_combined_total = pd.concat([df_cmi_mil_ano_total, df_cmi_ano_total])
        
        fig_comp_total = px.line(
            df_combined_total,
            x='Ano',
            y='Valor',
            color='Indicador',
            title=f"Total - Comparação ({anos_selecionados[0]}-{anos_selecionados[1]})",
            markers=True,
            color_discrete_map={
                'CMI-Mil (Total)': '#f59e0b',  # Laranja
                'CMI (Total)': '#0ea5e9'  # Azul
            }
        )
        fig_comp_total.update_layout(hovermode='x unified', height=500)
        st.plotly_chart(fig_comp_total, use_container_width=True)
        
        # Barras por estado
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("CMI-Mil por Estado")
            df_total_mil = df_cmi_mil_filtrado.groupby('UF')['Valor'].mean().reset_index().sort_values('Valor', ascending=False)
            fig_bar_mil = px.bar(df_total_mil, x='UF', y='Valor', title="Média CMI-Mil", color='UF', color_discrete_sequence=COLOR_SCALE)
            st.plotly_chart(fig_bar_mil, use_container_width=True)
        
        with col2:
            st.subheader("CMI por Estado")
            df_total_cmi = df_cmi_filtrado.groupby('UF')['Valor'].mean().reset_index().sort_values('Valor', ascending=False)
            fig_bar_cmi = px.bar(df_total_cmi, x='UF', y='Valor', title="Média CMI", color='UF', color_discrete_sequence=COLOR_SCALE)
            st.plotly_chart(fig_bar_cmi, use_container_width=True)
        
        # Tabela comparativa
        st.markdown("---")
        st.subheader("Tabela Comparativa")
        
        df_resumo_mil = df_cmi_mil_filtrado.groupby('UF')['Valor'].mean().reset_index()
        df_resumo_mil.columns = ['UF', 'CMI-Mil']
        df_resumo_mil['CMI-Mil'] = df_resumo_mil['CMI-Mil'].round(2)
        
        df_resumo_cmi = df_cmi_filtrado.groupby('UF')['Valor'].mean().reset_index()
        df_resumo_cmi.columns = ['UF', 'CMI']
        df_resumo_cmi['CMI'] = df_resumo_cmi['CMI'].round(2)
        
        df_resumo_comp = pd.merge(df_resumo_mil, df_resumo_cmi, on='UF')
        df_resumo_comp['Diferença'] = (df_resumo_comp['CMI-Mil'] - df_resumo_comp['CMI']).round(2)
        df_resumo_comp = df_resumo_comp.sort_values('CMI-Mil', ascending=False)
        
        st.dataframe(df_resumo_comp, use_container_width=True)
    
    else:  # CMI-Mil apenas
        df = carregar_dados_multiplas_ufs(ufs_selecionadas, 'CMI-Mil')
        
        if df is None or len(df) == 0:
            st.error("Não há dados de CMI-Mil para os estados selecionados")
            st.stop()
        
        anos_disponiveis = sorted(df['Ano'].unique())
        ano_min = int(min(anos_disponiveis))
        ano_max = int(max(anos_disponiveis))
        
        anos_selecionados = st.sidebar.slider(
            "Período",
            ano_min,
            ano_max,
            (ano_min, ano_max)
        )
        
        df_filtrado = df[
            (df['Ano'] >= anos_selecionados[0]) & 
            (df['Ano'] <= anos_selecionados[1])
        ]
        
        # ===== VISUALIZAÇÃO CMI-Mil =====
        st.title("Comparação entre Estados - CMI-Mil")
        st.markdown(f"### Análise de CMI-Mil - {len(ufs_selecionadas)} Estados")
        
        # Métricas
        st.markdown("---")
        cols = st.columns(min(len(ufs_selecionadas), 4))
        for idx, uf in enumerate(ufs_selecionadas[:4]):
            df_uf = df_filtrado[df_filtrado['UF'] == uf]
            total = df_uf['Valor'].mean()
            with cols[idx]:
                st.metric(uf, f"{total:.2f}")
        
        # Gráfico temporal
        st.markdown("---")
        st.subheader("Evolução Comparativa de CMI-Mil")
        
        df_comp_estados = df_filtrado.groupby(['Ano', 'UF'])['Valor'].mean().reset_index()
        
        fig_estados = px.line(
            df_comp_estados,
            x='Ano',
            y='Valor',
            color='UF',
            title=f"Comparação ({anos_selecionados[0]}-{anos_selecionados[1]})",
            markers=True,
            color_discrete_sequence=COLOR_SCALE
        )
        fig_estados.update_layout(hovermode='x unified')
        st.plotly_chart(fig_estados, use_container_width=True)
        
        # Barras e pizza
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Média por Estado")
            df_total = df_filtrado.groupby('UF')['Valor'].mean().reset_index().sort_values('Valor', ascending=False)
            fig_bar = px.bar(df_total, x='UF', y='Valor', color='UF', title="Média CMI-Mil", color_discrete_sequence=COLOR_SCALE)
            st.plotly_chart(fig_bar, use_container_width=True)
        
        with col2:
            st.subheader("Distribuição Percentual")
            fig_pie = px.pie(df_total, values='Valor', names='UF', title="Participação", color_discrete_sequence=COLOR_SCALE)
            st.plotly_chart(fig_pie, use_container_width=True)
        
        # Tabela
        st.markdown("---")
        st.subheader("Dados Comparativos")
        df_resumo = df_filtrado.groupby('UF')['Valor'].agg(['mean', 'min', 'max']).round(2)
        df_resumo.columns = ['Média', 'Mínimo', 'Máximo']
        st.dataframe(df_resumo, use_container_width=True)

# ====================================================================
# SEPARADOR
# ====================================================================

elif modo_visualizacao == "Nascidos Vivos e Óbitos":
    st.markdown("---")
    st.markdown("## 📊 Análise Original: Nascidos Vivos e Óbitos")
    st.markdown("---")
    
    # ====================================================================
    # SEÇÃO 2: ANÁLISE ORIGINAL (do código que o usuário passou)
    # ====================================================================
    
    st.sidebar.markdown("---")
    
    # Filtro de tipo de dado
    tipo_dado = st.sidebar.radio(
        "Tipo de Dado",
        ["Nascidos Vivos", "Óbitos"],
        index=0
    )
    
    tipo_cod = 'NV' if tipo_dado == "Nascidos Vivos" else 'OB'
    
    # Tipo de comparação
    tipo_comparacao = st.sidebar.radio(
        "Comparar por",
        ["Estados", "Municípios", "Estados e Municípios (Misto)"],
        index=0
    )
    
    if tipo_comparacao == "Estados":
        # Seleciona múltiplos estados
        ufs_selecionadas = st.sidebar.multiselect(
            "Selecione os Estados para Comparar",
            ufs_disponiveis,
            default=ufs_disponiveis[:3] if len(ufs_disponiveis) >= 3 else ufs_disponiveis
        )
        
        if not ufs_selecionadas:
            st.warning("Selecione pelo menos um estado para comparar")
            st.stop()
        
        # Carrega dados de todos os estados selecionados
        df = carregar_dados_multiplas_ufs(ufs_selecionadas, tipo_cod)
        
        if df is None or len(df) == 0:
            st.error(f"Não há dados de {tipo_dado} para os estados selecionados")
            st.stop()
        
        # Filtro de Anos
        anos_disponiveis = sorted(df['Ano'].unique())
        ano_min = int(min(anos_disponiveis))
        ano_max = int(max(anos_disponiveis))
        
        anos_selecionados = st.sidebar.slider(
            "Período",
            ano_min,
            ano_max,
            (ano_min, ano_max)
        )
        
        # Aplica filtros
        df_filtrado = df[
            (df['Ano'] >= anos_selecionados[0]) & 
            (df['Ano'] <= anos_selecionados[1])
        ]
        
        # ===== VISUALIZAÇÃO COMPARAÇÃO DE ESTADOS =====
        st.title("Comparação entre Estados")
        st.markdown(f"### Análise de {tipo_dado} - {len(ufs_selecionadas)} Estados")
        
        # Métricas por estado
        st.markdown("---")
        cols = st.columns(min(len(ufs_selecionadas), 4))
        for idx, uf in enumerate(ufs_selecionadas[:4]):
            df_uf = df_filtrado[df_filtrado['UF'] == uf]
            total = df_uf['Valor'].sum()
            with cols[idx]:
                st.metric(uf, f"{total:,.0f}".replace(",", "."))
        
        # Gráfico de comparação temporal
        st.markdown("---")
        st.subheader(f"Evolução Comparativa de {tipo_dado}")
        
        df_comp_estados = df_filtrado.groupby(['Ano', 'UF'])['Valor'].sum().reset_index()
        
        fig_estados = px.line(
            df_comp_estados,
            x='Ano',
            y='Valor',
            color='UF',
            title=f"Comparação de {tipo_dado} entre Estados ({anos_selecionados[0]}-{anos_selecionados[1]})",
            markers=True,
            labels={'Valor': f'Total de {tipo_dado}', 'UF': 'Estado'},
            color_discrete_sequence=COLOR_SCALE
        )
        fig_estados.update_layout(
            hovermode='x unified',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_estados, use_container_width=True)
        
        # Gráfico de barras comparativo
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Total por Estado")
            df_total_estados = df_filtrado.groupby('UF')['Valor'].sum().reset_index().sort_values('Valor', ascending=False)
            
            fig_bar = px.bar(
                df_total_estados,
                x='UF',
                y='Valor',
                color='UF',
                title=f"Total de {tipo_dado} por Estado",
                labels={'Valor': f'Total de {tipo_dado}', 'UF': 'Estado'},
                color_discrete_sequence=COLOR_SCALE
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        
        with col2:
            st.subheader("Distribuição Percentual")
            fig_pie = px.pie(
                df_total_estados,
                values='Valor',
                names='UF',
                title=f"Participação de cada Estado",
                color_discrete_sequence=COLOR_SCALE
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        # Tabela de dados
        st.markdown("---")
        st.subheader("Dados Comparativos")
        
        df_resumo = df_filtrado.groupby('UF').agg({
            'Valor': ['sum', 'mean', 'min', 'max'],
            'Municipio': 'nunique'
        }).round(0)
        df_resumo.columns = ['Total', 'Média', 'Mínimo', 'Máximo', 'Municípios']
        df_resumo = df_resumo.sort_values('Total', ascending=False)
        
        st.dataframe(df_resumo, use_container_width=True)
        
    elif tipo_comparacao == "Municípios":  # Comparação por Municípios
        # Primeiro seleciona estados
        ufs_para_municipios = st.sidebar.multiselect(
            "Estados (para listar municípios)",
            ufs_disponiveis,
            default=ufs_disponiveis[:2] if len(ufs_disponiveis) >= 2 else ufs_disponiveis
        )
        
        if not ufs_para_municipios:
            st.warning("Selecione pelo menos um estado")
            st.stop()
        
        # Carrega dados dos estados selecionados
        df_temp = carregar_dados_multiplas_ufs(ufs_para_municipios, tipo_cod)
        
        if df_temp is None or len(df_temp) == 0:
            st.error("Não há dados disponíveis")
            st.stop()
        
        # Aplica limpeza extra nos nomes de municípios para garantir remoção de números
        df_temp['Municipio'] = df_temp['Municipio'].apply(limpar_nome_municipio)
        df_temp = df_temp.dropna(subset=['Municipio'])
        
        # Lista municípios com UF
        df_temp['Municipio_UF'] = df_temp['Municipio'] + ' - ' + df_temp['UF']
        municipios_disponiveis = sorted(df_temp['Municipio_UF'].unique())
        
        # Seleciona municípios
        municipios_selecionados = st.sidebar.multiselect(
            "Selecione os Municípios para Comparar",
            municipios_disponiveis,
            default=municipios_disponiveis[:5] if len(municipios_disponiveis) >= 5 else municipios_disponiveis[:3]
        )
        
        if not municipios_selecionados:
            st.warning("Selecione pelo menos um município")
            st.stop()
        
        # Filtro de Anos
        anos_disponiveis = sorted(df_temp['Ano'].unique())
        ano_min = int(min(anos_disponiveis))
        ano_max = int(max(anos_disponiveis))
        
        anos_selecionados = st.sidebar.slider(
            "Período",
            ano_min,
            ano_max,
            (ano_min, ano_max)
        )
        
        # Filtra dados
        df_filtrado = df_temp[
            (df_temp['Municipio_UF'].isin(municipios_selecionados)) &
            (df_temp['Ano'] >= anos_selecionados[0]) & 
            (df_temp['Ano'] <= anos_selecionados[1])
        ]
        
        # ===== VISUALIZAÇÃO COMPARAÇÃO DE MUNICÍPIOS =====
        st.title("Comparação entre Municípios")
        st.markdown(f"### Análise de {tipo_dado} - {len(municipios_selecionados)} Municípios")
        
        # Métricas por município (top 4)
        st.markdown("---")
        cols = st.columns(min(len(municipios_selecionados), 4))
        for idx, mun in enumerate(municipios_selecionados[:4]):
            df_mun = df_filtrado[df_filtrado['Municipio_UF'] == mun]
            total = df_mun['Valor'].sum()
            with cols[idx]:
                st.metric(mun.split(' - ')[0][:15] + '...', f"{total:,.0f}".replace(",", "."))
        
        # Gráfico de comparação temporal
        st.markdown("---")
        st.subheader(f"Evolução Comparativa de {tipo_dado}")
        
        df_comp_mun = df_filtrado.groupby(['Ano', 'Municipio_UF'])['Valor'].sum().reset_index()
        
        fig_mun = px.line(
            df_comp_mun,
            x='Ano',
            y='Valor',
            color='Municipio_UF',
            title=f"Comparação de {tipo_dado} entre Municípios ({anos_selecionados[0]}-{anos_selecionados[1]})",
            markers=True,
            labels={'Valor': f'Total de {tipo_dado}', 'Municipio_UF': 'Município'},
            color_discrete_sequence=COLOR_SCALE
        )
        fig_mun.update_layout(
            hovermode='x unified',
            legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02)
        )
        st.plotly_chart(fig_mun, use_container_width=True)
        
        # Gráfico de barras comparativo
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Total por Município")
            df_total_mun = df_filtrado.groupby('Municipio_UF')['Valor'].sum().reset_index().sort_values('Valor', ascending=False)
            
            fig_bar_mun = px.bar(
                df_total_mun,
                y='Municipio_UF',
                x='Valor',
                orientation='h',
                color='Municipio_UF',
                title=f"Total de {tipo_dado} por Município",
                labels={'Valor': f'Total de {tipo_dado}', 'Municipio_UF': 'Município'},
                color_discrete_sequence=COLOR_SCALE
            )
            fig_bar_mun.update_layout(showlegend=False, yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig_bar_mun, use_container_width=True)
        
        with col2:
            st.subheader("Média Anual")
            df_media_mun = df_filtrado.groupby('Municipio_UF')['Valor'].mean().reset_index().sort_values('Valor', ascending=False)
            
            fig_media = px.bar(
                df_media_mun,
                y='Municipio_UF',
                x='Valor',
                orientation='h',
                color='Municipio_UF',
                title="Média Anual por Município",
                labels={'Valor': 'Média Anual', 'Municipio_UF': 'Município'},
                color_discrete_sequence=COLOR_SCALE
            )
            fig_media.update_layout(showlegend=False, yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig_media, use_container_width=True)
        
        # Tabela de dados
        st.markdown("---")
        st.subheader("Dados Comparativos")
        
        df_resumo_mun = df_filtrado.groupby(['Municipio_UF', 'UF']).agg({
            'Valor': ['sum', 'mean', 'min', 'max']
        }).round(0)
        df_resumo_mun.columns = ['Total', 'Média Anual', 'Mínimo', 'Máximo']
        df_resumo_mun = df_resumo_mun.sort_values('Total', ascending=False)
        
        st.dataframe(df_resumo_mun, use_container_width=True)
        
        # Download
        csv = df_filtrado.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="Baixar dados comparativos em CSV",
            data=csv,
            file_name=f"comparacao_municipios_{tipo_cod}_{anos_selecionados[0]}-{anos_selecionados[1]}.csv",
            mime="text/csv"
        )
    
    else:  # Comparação Mista (Estados e Municípios)
        st.info("💡 **Comparação Flexível**: Selecione estados inteiros e/ou municípios específicos de qualquer estado para comparar!")
        
        # Carrega todos os dados disponíveis
        df_todos = carregar_dados_multiplas_ufs(ufs_disponiveis, tipo_cod)
        
        if df_todos is None or len(df_todos) == 0:
            st.error("Não há dados disponíveis")
            st.stop()
        
        # Aplica limpeza extra nos nomes de municípios para garantir remoção de números
        df_todos['Municipio'] = df_todos['Municipio'].apply(limpar_nome_municipio)
        df_todos = df_todos.dropna(subset=['Municipio'])
        
        # Cria opções de seleção
        opcoes_comparacao = []
        
        # Adiciona estados como opção (agregado total)
        for uf in ufs_disponiveis:
            opcoes_comparacao.append(f"ESTADO: {uf}")
        
        # Adiciona municípios de todos os estados
        df_todos['Municipio_UF'] = df_todos['Municipio'] + ' - ' + df_todos['UF']
        municipios_todos = sorted(df_todos['Municipio_UF'].unique())
        
        for mun in municipios_todos:
            opcoes_comparacao.append(f"MUNICÍPIO: {mun}")
        
        # Seleção flexível
        selecoes = st.sidebar.multiselect(
            "Selecione Estados e/ou Municípios para Comparar",
            opcoes_comparacao,
            default=[]
        )
        
        if not selecoes:
            st.warning("Selecione pelo menos um estado ou município para comparar")
            st.stop()
        
        # Filtro de Anos
        anos_disponiveis = sorted(df_todos['Ano'].unique())
        ano_min = int(min(anos_disponiveis))
        ano_max = int(max(anos_disponiveis))
        
        anos_selecionados = st.sidebar.slider(
            "Período",
            ano_min,
            ano_max,
            (ano_min, ano_max)
        )
        
        # Processa seleções e agrupa dados
        dados_comparacao = []
        
        for selecao in selecoes:
            if selecao.startswith("ESTADO:"):
                uf = selecao.replace("ESTADO: ", "")
                df_temp = df_todos[
                    (df_todos['UF'] == uf) &
                    (df_todos['Ano'] >= anos_selecionados[0]) & 
                    (df_todos['Ano'] <= anos_selecionados[1])
                ]
                df_agrupado = df_temp.groupby('Ano')['Valor'].sum().reset_index()
                df_agrupado['Entidade'] = f"Estado: {uf}"
                dados_comparacao.append(df_agrupado)
            else:  # MUNICÍPIO
                mun_uf = selecao.replace("MUNICÍPIO: ", "")
                df_temp = df_todos[
                    (df_todos['Municipio_UF'] == mun_uf) &
                    (df_todos['Ano'] >= anos_selecionados[0]) & 
                    (df_todos['Ano'] <= anos_selecionados[1])
                ]
                df_agrupado = df_temp.groupby('Ano')['Valor'].sum().reset_index()
                df_agrupado['Entidade'] = f"Mun: {mun_uf.split(' - ')[0][:20]}"
                dados_comparacao.append(df_agrupado)
        
        # Combina todos os dados
        if not dados_comparacao:
            st.error("Nenhum dado encontrado para as seleções")
            st.stop()
        
        df_combinado = pd.concat(dados_comparacao, ignore_index=True)
        
        # ===== VISUALIZAÇÃO COMPARAÇÃO MISTA =====
        st.title("Comparação Customizada: Estados e Municípios")
        st.markdown(f"### Análise de {tipo_dado} - {len(selecoes)} Entidades Selecionadas")
        
        # Métricas (top 4)
        st.markdown("---")
        cols = st.columns(min(len(selecoes), 4))
        for idx, selecao in enumerate(selecoes[:4]):
            entidade_nome = selecao.replace("ESTADO: ", "").replace("MUNICÍPIO: ", "")
            df_ent = df_combinado[df_combinado['Entidade'].str.contains(entidade_nome.split(' - ')[0][:15])]
            total = df_ent['Valor'].sum()
            nome_curto = entidade_nome.split(' - ')[0][:12]
            with cols[idx]:
                st.metric(nome_curto, f"{total:,.0f}".replace(",", "."))
        
        # Gráfico de comparação temporal
        st.markdown("---")
        st.subheader(f"Evolução Comparativa de {tipo_dado}")
        
        fig_misto = px.line(
            df_combinado,
            x='Ano',
            y='Valor',
            color='Entidade',
            title=f"Comparação Mista ({anos_selecionados[0]}-{anos_selecionados[1]})",
            markers=True,
            labels={'Valor': f'Total de {tipo_dado}', 'Entidade': 'Estado/Município'},
            color_discrete_sequence=COLOR_SCALE
        )
        fig_misto.update_layout(
            hovermode='x unified',
            legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02)
        )
        st.plotly_chart(fig_misto, use_container_width=True)
        
        # Gráfico de barras comparativo
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Total Comparativo")
            df_total_misto = df_combinado.groupby('Entidade')['Valor'].sum().reset_index().sort_values('Valor', ascending=False)
            
            fig_bar_misto = px.bar(
                df_total_misto,
                y='Entidade',
                x='Valor',
                orientation='h',
                color='Entidade',
                title=f"Total de {tipo_dado}",
                labels={'Valor': f'Total de {tipo_dado}', 'Entidade': 'Estado/Município'},
                color_discrete_sequence=COLOR_SCALE
            )
            fig_bar_misto.update_layout(showlegend=False, yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig_bar_misto, use_container_width=True)
        
        with col2:
            st.subheader("Média Anual")
            df_media_misto = df_combinado.groupby('Entidade')['Valor'].mean().reset_index().sort_values('Valor', ascending=False)
            
            fig_media_misto = px.bar(
                df_media_misto,
                y='Entidade',
                x='Valor',
                orientation='h',
                color='Entidade',
                title="Média Anual",
                labels={'Valor': 'Média Anual', 'Entidade': 'Estado/Município'},
                color_discrete_sequence=COLOR_SCALE
            )
            fig_media_misto.update_layout(showlegend=False, yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig_media_misto, use_container_width=True)
        
        # Tabela de dados
        st.markdown("---")
        st.subheader("Dados Comparativos")
        
        df_resumo_misto = df_combinado.groupby('Entidade').agg({
            'Valor': ['sum', 'mean', 'min', 'max']
        }).round(0)
        df_resumo_misto.columns = ['Total', 'Média Anual', 'Mínimo', 'Máximo']
        df_resumo_misto = df_resumo_misto.sort_values('Total', ascending=False)
        
        st.dataframe(df_resumo_misto, use_container_width=True)
        
        # Download
        csv = df_combinado.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="Baixar dados comparativos em CSV",
            data=csv,
            file_name=f"comparacao_mista_{tipo_cod}_{anos_selecionados[0]}-{anos_selecionados[1]}.csv",
            mime="text/csv"
        )

# Rodapé
st.markdown("---")
st.markdown("**Dashboard de Saúde Pública** | Dados de CMI-Mil, CMI, Nascidos Vivos e Óbitos")
