"""
Dashboard Streamlit para visualização de dados de Nascidos Vivos e Óbitos por UF
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from pathlib import Path

# Configuração da página
st.set_page_config(
    page_title="Dashboard Saúde - Nascimentos e Óbitos",
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
BASE_DIR = Path(__file__).parent  # app.py está na raiz
DIR_NV = BASE_DIR / 'data' / 'output' / 'nascidos_vivos'
DIR_OB = BASE_DIR / 'data' / 'output' / 'obitos'
DIR_CMI_MIL = BASE_DIR / 'data' / 'output' / 'CMI_MIL'
DIR_CMI_PURO = BASE_DIR / 'data' / 'output' / 'CMI_puro'

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

# Cache dos dados
@st.cache_data
def carregar_dados_uf(uf, tipo):
    """
    Carrega dados de uma UF específica (NV, OB, CMI_MIL ou CMI_puro)
    """
    if tipo == 'CMI_MIL':
        diretorio = DIR_CMI_MIL
    elif tipo == 'CMI_puro':
        diretorio = DIR_CMI_PURO
    elif tipo == 'NV':
        diretorio = DIR_NV
    else:
        diretorio = DIR_OB
    arquivo = diretorio / f"{uf}.json"
    
    if not arquivo.exists():
        return None
    
    with open(arquivo, 'r', encoding='utf-8') as f:
        dados = json.load(f)
    
    df = pd.DataFrame(dados)
    return df

@st.cache_data
def listar_ufs_disponiveis():
    """
    Lista todas as UFs que têm dados disponíveis (ordenadas alfabeticamente)
    """
    ufs = []
    for arquivo in DIR_OB.glob("*.json"):
        uf = arquivo.stem
        ufs.append(uf)
    return sorted(ufs)  # Ordem alfabética

@st.cache_data
def listar_ufs_cmi_disponiveis():
    """
    Lista todas as UFs que têm dados CMI_MIL disponíveis
    """
    ufs = []
    if DIR_CMI_MIL.exists():
        for arquivo in DIR_CMI_MIL.glob("*.json"):
            uf = arquivo.stem
            ufs.append(uf)
    return sorted(ufs)

@st.cache_data
def listar_ufs_cmi_puro_disponiveis():
    """
    Lista todas as UFs que têm dados CMI_puro disponíveis
    """
    ufs = []
    if DIR_CMI_PURO.exists():
        for arquivo in DIR_CMI_PURO.glob("*.json"):
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
st.title("📊 Dashboard de Saúde Pública")
st.markdown("### 🏥 Análise de Nascidos Vivos e Óbitos por Município e Estado")
st.markdown("---")

# Sidebar
st.sidebar.header("Filtros")

# Modo de visualização
modo_visualizacao = st.sidebar.radio(
    "Modo de Visualização",
    ["Estado Individual", "Comparação", "CMI_MIL", "CMI_puro", "Comparação CMI"],
    index=0
)

# Verifica se há dados disponíveis
ufs_disponiveis = listar_ufs_disponiveis()

if not ufs_disponiveis:
    st.error("Nenhum dado encontrado! Execute primeiro o script converter_dados.py")
    st.stop()

# ===== MODO COMPARAÇÃO =====
if modo_visualizacao == "Comparação":
    st.sidebar.markdown("---")
    
    # Tipo de comparação
    tipo_comparacao = st.sidebar.radio(
        "Comparar por",
        ["Estados", "Municípios"],
        index=0
    )
    
    # Filtro de tipo de dado
    tipo_dado = st.sidebar.radio(
        "Tipo de Dado",
        ["Nascidos Vivos", "Óbitos"],
        index=0
    )
    
    tipo_cod = 'NV' if tipo_dado == "Nascidos Vivos" else 'OB'
    
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
        st.title("🌎 Comparação entre Estados")
        st.markdown(f"### 📊 Análise de {tipo_dado} - {len(ufs_selecionadas)} Estados")
        
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
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=12)
        )
        fig_estados.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#e5e7eb')
        fig_estados.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#e5e7eb')
        st.plotly_chart(fig_estados, width='stretch')
        
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
            fig_bar.update_layout(
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            fig_bar.update_xaxes(showgrid=False)
            fig_bar.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#e5e7eb')
            st.plotly_chart(fig_bar, width='stretch')
        
        with col2:
            st.subheader("Distribuição Percentual")
            fig_pie = px.pie(
                df_total_estados,
                values='Valor',
                names='UF',
                title=f"Participação de cada Estado",
                color_discrete_sequence=COLOR_SCALE
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            fig_pie.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_pie, width='stretch')
        
        # Tabela de dados
        st.markdown("---")
        st.subheader("Dados Comparativos")
        
        df_resumo = df_filtrado.groupby('UF').agg({
            'Valor': ['sum', 'mean', 'min', 'max'],
            'Municipio': 'nunique'
        }).round(0)
        df_resumo.columns = ['Total', 'Média', 'Mínimo', 'Máximo', 'Municípios']
        df_resumo = df_resumo.sort_values('Total', ascending=False)
        
        st.dataframe(df_resumo, width='stretch')
        
    else:  # Comparação por Municípios
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
            labels={'Valor': f'Total de {tipo_dado}', 'Municipio_UF': 'Município'}
        )
        fig_mun.update_layout(
            hovermode='x unified',
            legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02)
        )
        st.plotly_chart(fig_mun, width='stretch')
        
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
                labels={'Valor': f'Total de {tipo_dado}', 'Municipio_UF': 'Município'}
            )
            fig_bar_mun.update_layout(showlegend=False, yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig_bar_mun, width='stretch')
        
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
                labels={'Valor': 'Média Anual', 'Municipio_UF': 'Município'}
            )
            fig_media.update_layout(showlegend=False, yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig_media, width='stretch')
        
        # Tabela de dados
        st.markdown("---")
        st.subheader("Dados Comparativos")
        
        df_resumo_mun = df_filtrado.groupby(['Municipio_UF', 'UF']).agg({
            'Valor': ['sum', 'mean', 'min', 'max']
        }).round(0)
        df_resumo_mun.columns = ['Total', 'Média Anual', 'Mínimo', 'Máximo']
        df_resumo_mun = df_resumo_mun.sort_values('Total', ascending=False)
        
        st.dataframe(df_resumo_mun, width='stretch')
        
        # Download
        csv = df_filtrado.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="Baixar dados comparativos em CSV",
            data=csv,
            file_name=f"comparacao_municipios_{tipo_cod}_{anos_selecionados[0]}-{anos_selecionados[1]}.csv",
            mime="text/csv"
        )

# ===== MODO CMI_MIL =====
elif modo_visualizacao == "CMI_MIL":
    st.sidebar.markdown("---")
    
    # Verifica se há dados CMI_MIL disponíveis
    ufs_cmi_disponiveis = listar_ufs_cmi_disponiveis()
    
    if not ufs_cmi_disponiveis:
        st.warning("Nenhum dado CMI_MIL encontrado! Execute primeiro o script converter_dados.py")
        st.info("Os dados CMI_MIL são extraídos de abas que começam com 'CMI_' na planilha.")
        st.stop()
    
    # Tipo de comparação CMI
    tipo_comparacao_cmi = st.sidebar.radio(
        "Comparar por",
        ["Estados", "Municípios"],
        index=0
    )
    
    if tipo_comparacao_cmi == "Estados":
        # Seleciona múltiplos estados CMI_MIL
        ufs_cmi_selecionadas = st.sidebar.multiselect(
            "Selecione os Estados CMI_MIL para Comparar",
            ufs_cmi_disponiveis,
            default=ufs_cmi_disponiveis[:3] if len(ufs_cmi_disponiveis) >= 3 else ufs_cmi_disponiveis
        )
        
        if not ufs_cmi_selecionadas:
            st.warning("Selecione pelo menos um estado para comparar")
            st.stop()
        
        # Carrega dados de todos os estados selecionados
        df_cmi = carregar_dados_multiplas_ufs(ufs_cmi_selecionadas, 'CMI_MIL')
        
        if df_cmi is None or len(df_cmi) == 0:
            st.error(f"Não há dados CMI_MIL para os estados selecionados")
            st.stop()
        
        # Filtro de Anos
        anos_disponiveis = sorted(df_cmi['Ano'].unique())
        ano_min = int(min(anos_disponiveis))
        ano_max = int(max(anos_disponiveis))
        
        anos_selecionados = st.sidebar.slider(
            "Período",
            ano_min,
            ano_max,
            (ano_min, ano_max)
        )
        
        # Aplica filtros
        df_cmi_filtrado = df_cmi[
            (df_cmi['Ano'] >= anos_selecionados[0]) & 
            (df_cmi['Ano'] <= anos_selecionados[1])
        ]
        
        # ===== VISUALIZAÇÃO COMPARAÇÃO DE ESTADOS CMI_MIL =====
        st.title("Comparação entre Estados - Dados CMI_MIL")
        st.markdown(f"### Análise de Dados CMI_MIL - {len(ufs_cmi_selecionadas)} Estados")
        
        # Métricas por estado
        st.markdown("---")
        cols = st.columns(min(len(ufs_cmi_selecionadas), 4))
        for idx, uf in enumerate(ufs_cmi_selecionadas[:4]):
            df_uf = df_cmi_filtrado[df_cmi_filtrado['UF'] == uf]
            total = df_uf['Valor'].sum()
            with cols[idx]:
                st.metric(uf, f"{total:,.0f}".replace(",", "."))
        
        # Gráfico de comparação temporal
        st.markdown("---")
        st.subheader(f"Evolução Comparativa de Dados CMI_MIL")
        
        df_comp_estados_cmi = df_cmi_filtrado.groupby(['Ano', 'UF'])['Valor'].sum().reset_index()
        
        fig_estados_cmi = px.line(
            df_comp_estados_cmi,
            x='Ano',
            y='Valor',
            color='UF',
            title=f"Comparação de Dados CMI_MIL entre Estados ({anos_selecionados[0]}-{anos_selecionados[1]})",
            markers=True,
            labels={'Valor': 'Total CMI_MIL', 'UF': 'Estado'},
            color_discrete_sequence=COLOR_SCALE
        )
        fig_estados_cmi.update_layout(
            hovermode='x unified',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_estados_cmi, width='stretch')
        
        # Gráfico de barras comparativo
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Total por Estado")
            df_total_estados_cmi = df_cmi_filtrado.groupby('UF')['Valor'].sum().reset_index().sort_values('Valor', ascending=False)
            
            fig_bar_cmi = px.bar(
                df_total_estados_cmi,
                x='UF',
                y='Valor',
                color='UF',
                title=f"Total de Dados CMI por Estado",
                labels={'Valor': 'Total CMI', 'UF': 'Estado'},
                color_discrete_sequence=COLOR_SCALE
            )
            fig_bar_cmi.update_layout(
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            fig_bar_cmi.update_xaxes(showgrid=False)
            fig_bar_cmi.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#334155')
            st.plotly_chart(fig_bar_cmi, width='stretch')
        
        with col2:
            st.subheader("Distribuição Percentual")
            fig_pie_cmi = px.pie(
                df_total_estados_cmi,
                values='Valor',
                names='UF',
                title=f"Participação de cada Estado",
                color_discrete_sequence=COLOR_SCALE
            )
            fig_pie_cmi.update_traces(textposition='inside', textinfo='percent+label')
            fig_pie_cmi.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_pie_cmi, width='stretch')
        
        # Tabela de dados
        st.markdown("---")
        st.subheader("Dados Comparativos CMI")
        
        df_resumo_cmi = df_cmi_filtrado.groupby('UF').agg({
            'Valor': ['sum', 'mean', 'min', 'max'],
            'Municipio': 'nunique'
        }).round(0)
        df_resumo_cmi.columns = ['Total', 'Média', 'Mínimo', 'Máximo', 'Municípios']
        df_resumo_cmi = df_resumo_cmi.sort_values('Total', ascending=False)
        
        st.dataframe(df_resumo_cmi, width='stretch')
        
    else:  # Comparação por Municípios CMI
        # Primeiro seleciona estados
        ufs_cmi_para_municipios = st.sidebar.multiselect(
            "Estados (para listar municípios)",
            ufs_cmi_disponiveis,
            default=ufs_cmi_disponiveis[:2] if len(ufs_cmi_disponiveis) >= 2 else ufs_cmi_disponiveis
        )
        
        if not ufs_cmi_para_municipios:
            st.warning("Selecione pelo menos um estado")
            st.stop()
        
        # Carrega dados dos estados selecionados
        df_cmi_temp = carregar_dados_multiplas_ufs(ufs_cmi_para_municipios, 'CMI')
        
        if df_cmi_temp is None or len(df_cmi_temp) == 0:
            st.error("Não há dados disponíveis")
            st.stop()
        
        # Lista municípios com UF
        df_cmi_temp['Municipio_UF'] = df_cmi_temp['Municipio'] + ' - ' + df_cmi_temp['UF']
        municipios_cmi_disponiveis = sorted(df_cmi_temp['Municipio_UF'].unique())
        
        # Seleciona municípios
        municipios_cmi_selecionados = st.sidebar.multiselect(
            "Selecione os Municípios para Comparar",
            municipios_cmi_disponiveis,
            default=municipios_cmi_disponiveis[:5] if len(municipios_cmi_disponiveis) >= 5 else municipios_cmi_disponiveis[:3]
        )
        
        if not municipios_cmi_selecionados:
            st.warning("Selecione pelo menos um município")
            st.stop()
        
        # Filtro de Anos
        anos_disponiveis = sorted(df_cmi_temp['Ano'].unique())
        ano_min = int(min(anos_disponiveis))
        ano_max = int(max(anos_disponiveis))
        
        anos_selecionados = st.sidebar.slider(
            "Período",
            ano_min,
            ano_max,
            (ano_min, ano_max)
        )
        
        # Filtra dados
        df_cmi_filtrado = df_cmi_temp[
            (df_cmi_temp['Municipio_UF'].isin(municipios_cmi_selecionados)) &
            (df_cmi_temp['Ano'] >= anos_selecionados[0]) & 
            (df_cmi_temp['Ano'] <= anos_selecionados[1])
        ]
        
        # ===== VISUALIZAÇÃO COMPARAÇÃO DE MUNICÍPIOS CMI =====
        st.title("Comparação entre Municípios - Dados CMI")
        st.markdown(f"### Análise de Dados CMI - {len(municipios_cmi_selecionados)} Municípios")
        
        # Métricas por município (top 4)
        st.markdown("---")
        cols = st.columns(min(len(municipios_cmi_selecionados), 4))
        for idx, mun in enumerate(municipios_cmi_selecionados[:4]):
            df_mun = df_cmi_filtrado[df_cmi_filtrado['Municipio_UF'] == mun]
            total = df_mun['Valor'].sum()
            with cols[idx]:
                st.metric(mun.split(' - ')[0][:15] + '...', f"{total:,.0f}".replace(",", "."))
        
        # Gráfico de comparação temporal
        st.markdown("---")
        st.subheader(f"Evolução Comparativa de Dados CMI")
        
        df_comp_mun_cmi = df_cmi_filtrado.groupby(['Ano', 'Municipio_UF'])['Valor'].sum().reset_index()
        
        fig_mun_cmi = px.line(
            df_comp_mun_cmi,
            x='Ano',
            y='Valor',
            color='Municipio_UF',
            title=f"Comparação de Dados CMI entre Municípios ({anos_selecionados[0]}-{anos_selecionados[1]})",
            markers=True,
            labels={'Valor': 'Total CMI', 'Municipio_UF': 'Município'},
            color_discrete_sequence=COLOR_SCALE
        )
        fig_mun_cmi.update_layout(
            hovermode='x unified',
            legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02)
        )
        st.plotly_chart(fig_mun_cmi, width='stretch')
        
        # Gráfico de barras comparativo
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Total por Município")
            df_total_mun_cmi = df_cmi_filtrado.groupby('Municipio_UF')['Valor'].sum().reset_index().sort_values('Valor', ascending=False)
            
            fig_bar_mun_cmi = px.bar(
                df_total_mun_cmi,
                y='Municipio_UF',
                x='Valor',
                orientation='h',
                color='Municipio_UF',
                title=f"Total de Dados CMI por Município",
                labels={'Valor': 'Total CMI', 'Municipio_UF': 'Município'},
                color_discrete_sequence=COLOR_SCALE
            )
            fig_bar_mun_cmi.update_layout(showlegend=False, yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig_bar_mun_cmi, width='stretch')
        
        with col2:
            st.subheader("Média Anual")
            df_media_mun_cmi = df_cmi_filtrado.groupby('Municipio_UF')['Valor'].mean().reset_index().sort_values('Valor', ascending=False)
            
            fig_media_cmi = px.bar(
                df_media_mun_cmi,
                y='Municipio_UF',
                x='Valor',
                orientation='h',
                color='Municipio_UF',
                title="Média Anual por Município",
                labels={'Valor': 'Média Anual', 'Municipio_UF': 'Município'},
                color_discrete_sequence=COLOR_SCALE
            )
            fig_media_cmi.update_layout(showlegend=False, yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig_media_cmi, width='stretch')
        
        # Tabela de dados
        st.markdown("---")
        st.subheader("Dados Comparativos CMI")
        
        df_resumo_mun_cmi = df_cmi_filtrado.groupby(['Municipio_UF', 'UF']).agg({
            'Valor': ['sum', 'mean', 'min', 'max']
        }).round(0)
        df_resumo_mun_cmi.columns = ['Total', 'Média Anual', 'Mínimo', 'Máximo']
        df_resumo_mun_cmi = df_resumo_mun_cmi.sort_values('Total', ascending=False)
        
        st.dataframe(df_resumo_mun_cmi, width='stretch')
        
        # Download
        csv = df_cmi_filtrado.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="Baixar dados comparativos em CSV",
            data=csv,
            file_name=f"comparacao_municipios_CMI_MIL_{anos_selecionados[0]}-{anos_selecionados[1]}.csv",
            mime="text/csv"
        )

# ===== MODO CMI_puro =====
elif modo_visualizacao == "CMI_puro":
    st.sidebar.markdown("---")
    
    # Verifica se há dados CMI_puro disponíveis
    ufs_cmi_puro_disponiveis = listar_ufs_cmi_puro_disponiveis()
    
    if not ufs_cmi_puro_disponiveis:
        st.warning("Nenhum dado CMI_puro encontrado! Execute primeiro o script converter_dados.py")
        st.info("Os dados CMI_puro são extraídos da planilha CMI_PURO_semMIL.xlsx")
        st.stop()
    
    # Tipo de comparação CMI_puro
    tipo_comparacao_cmi_puro = st.sidebar.radio(
        "Comparar por",
        ["Estados", "Municípios"],
        index=0
    )
    
    if tipo_comparacao_cmi_puro == "Estados":
        # Seleciona múltiplos estados CMI_puro
        ufs_cmi_puro_selecionadas = st.sidebar.multiselect(
            "Selecione os Estados CMI_puro para Comparar",
            ufs_cmi_puro_disponiveis,
            default=ufs_cmi_puro_disponiveis[:3] if len(ufs_cmi_puro_disponiveis) >= 3 else ufs_cmi_puro_disponiveis
        )
        
        if not ufs_cmi_puro_selecionadas:
            st.warning("Selecione pelo menos um estado para comparar")
            st.stop()
        
        # Carrega dados de todos os estados selecionados
        df_cmi_puro = carregar_dados_multiplas_ufs(ufs_cmi_puro_selecionadas, 'CMI_puro')
        
        if df_cmi_puro is None or len(df_cmi_puro) == 0:
            st.error(f"Não há dados CMI_puro para os estados selecionados")
            st.stop()
        
        # Filtro de Anos
        anos_disponiveis = sorted(df_cmi_puro['Ano'].unique())
        ano_min = int(min(anos_disponiveis))
        ano_max = int(max(anos_disponiveis))
        
        anos_selecionados = st.sidebar.slider(
            "Período",
            ano_min,
            ano_max,
            (ano_min, ano_max)
        )
        
        # Aplica filtros
        df_cmi_puro_filtrado = df_cmi_puro[
            (df_cmi_puro['Ano'] >= anos_selecionados[0]) & 
            (df_cmi_puro['Ano'] <= anos_selecionados[1])
        ]
        
        # ===== VISUALIZAÇÃO COMPARAÇÃO DE ESTADOS CMI_puro =====
        st.title("Comparação entre Estados - Dados CMI_puro")
        st.markdown(f"### Análise de Dados CMI_puro - {len(ufs_cmi_puro_selecionadas)} Estados")
        
        # Métricas por estado
        st.markdown("---")
        cols = st.columns(min(len(ufs_cmi_puro_selecionadas), 4))
        for idx, uf in enumerate(ufs_cmi_puro_selecionadas[:4]):
            df_uf = df_cmi_puro_filtrado[df_cmi_puro_filtrado['UF'] == uf]
            total = df_uf['Valor'].sum()
            with cols[idx]:
                st.metric(uf, f"{total:,.0f}".replace(",", "."))
        
        # Gráfico de comparação temporal
        st.markdown("---")
        st.subheader(f"Evolução Comparativa de Dados CMI_puro")
        
        df_comp_estados_puro = df_cmi_puro_filtrado.groupby(['Ano', 'UF'])['Valor'].sum().reset_index()
        
        fig_estados_puro = px.line(
            df_comp_estados_puro,
            x='Ano',
            y='Valor',
            color='UF',
            title=f"Comparação de Dados CMI_puro entre Estados ({anos_selecionados[0]}-{anos_selecionados[1]})",
            markers=True,
            labels={'Valor': 'Total CMI_puro', 'UF': 'Estado'},
            color_discrete_sequence=COLOR_SCALE
        )
        fig_estados_puro.update_layout(
            hovermode='x unified',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_estados_puro, width='stretch')
        
        # Gráfico de barras comparativo
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Total por Estado")
            df_total_estados_puro = df_cmi_puro_filtrado.groupby('UF')['Valor'].sum().reset_index().sort_values('Valor', ascending=False)
            
            fig_bar_puro = px.bar(
                df_total_estados_puro,
                x='UF',
                y='Valor',
                color='UF',
                title=f"Total de Dados CMI_puro por Estado",
                labels={'Valor': 'Total CMI_puro', 'UF': 'Estado'},
                color_discrete_sequence=COLOR_SCALE
            )
            fig_bar_puro.update_layout(showlegend=False)
            st.plotly_chart(fig_bar_puro, width='stretch')
        
        with col2:
            st.subheader("Distribuição Percentual")
            fig_pie_puro = px.pie(
                df_total_estados_puro,
                values='Valor',
                names='UF',
                title=f"Participação de cada Estado",
                color_discrete_sequence=COLOR_SCALE
            )
            fig_pie_puro.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie_puro, width='stretch')
        
        # Tabela de dados
        st.markdown("---")
        st.subheader("Dados Comparativos CMI_puro")
        
        df_resumo_puro = df_cmi_puro_filtrado.groupby('UF').agg({
            'Valor': ['sum', 'mean', 'min', 'max'],
            'Municipio': 'nunique'
        }).round(0)
        df_resumo_puro.columns = ['Total', 'Média', 'Mínimo', 'Máximo', 'Municípios']
        df_resumo_puro = df_resumo_puro.sort_values('Total', ascending=False)
        
        st.dataframe(df_resumo_puro, width='stretch')
        
    else:  # Comparação por Municípios CMI_puro
        # Primeiro seleciona estados
        ufs_puro_para_municipios = st.sidebar.multiselect(
            "Estados (para listar municípios)",
            ufs_cmi_puro_disponiveis,
            default=ufs_cmi_puro_disponiveis[:2] if len(ufs_cmi_puro_disponiveis) >= 2 else ufs_cmi_puro_disponiveis
        )
        
        if not ufs_puro_para_municipios:
            st.warning("Selecione pelo menos um estado")
            st.stop()
        
        # Carrega dados dos estados selecionados
        df_puro_temp = carregar_dados_multiplas_ufs(ufs_puro_para_municipios, 'CMI_puro')
        
        if df_puro_temp is None or len(df_puro_temp) == 0:
            st.error("Não há dados disponíveis")
            st.stop()
        
        # Lista municípios com UF
        df_puro_temp['Municipio_UF'] = df_puro_temp['Municipio'] + ' - ' + df_puro_temp['UF']
        municipios_puro_disponiveis = sorted(df_puro_temp['Municipio_UF'].unique())
        
        # Seleciona municípios
        municipios_puro_selecionados = st.sidebar.multiselect(
            "Selecione os Municípios para Comparar",
            municipios_puro_disponiveis,
            default=municipios_puro_disponiveis[:5] if len(municipios_puro_disponiveis) >= 5 else municipios_puro_disponiveis[:3]
        )
        
        if not municipios_puro_selecionados:
            st.warning("Selecione pelo menos um município")
            st.stop()
        
        # Filtro de Anos
        anos_disponiveis = sorted(df_puro_temp['Ano'].unique())
        ano_min = int(min(anos_disponiveis))
        ano_max = int(max(anos_disponiveis))
        
        anos_selecionados = st.sidebar.slider(
            "Período",
            ano_min,
            ano_max,
            (ano_min, ano_max)
        )
        
        # Filtra dados
        df_puro_filtrado = df_puro_temp[
            (df_puro_temp['Municipio_UF'].isin(municipios_puro_selecionados)) &
            (df_puro_temp['Ano'] >= anos_selecionados[0]) & 
            (df_puro_temp['Ano'] <= anos_selecionados[1])
        ]
        
        # ===== VISUALIZAÇÃO COMPARAÇÃO DE MUNICÍPIOS CMI_puro =====
        st.title("Comparação entre Municípios - Dados CMI_puro")
        st.markdown(f"### Análise de Dados CMI_puro - {len(municipios_puro_selecionados)} Municípios")
        
        # Métricas por município (top 4)
        st.markdown("---")
        cols = st.columns(min(len(municipios_puro_selecionados), 4))
        for idx, mun in enumerate(municipios_puro_selecionados[:4]):
            df_mun = df_puro_filtrado[df_puro_filtrado['Municipio_UF'] == mun]
            total = df_mun['Valor'].sum()
            with cols[idx]:
                st.metric(mun.split(' - ')[0][:15] + '...', f"{total:,.0f}".replace(",", "."))
        
        # Gráfico de comparação temporal
        st.markdown("---")
        st.subheader(f"Evolução Comparativa de Dados CMI_puro")
        
        df_comp_mun_puro = df_puro_filtrado.groupby(['Ano', 'Municipio_UF'])['Valor'].sum().reset_index()
        
        fig_mun_puro = px.line(
            df_comp_mun_puro,
            x='Ano',
            y='Valor',
            color='Municipio_UF',
            title=f"Comparação de Dados CMI_puro entre Municípios ({anos_selecionados[0]}-{anos_selecionados[1]})",
            markers=True,
            labels={'Valor': 'Total CMI_puro', 'Municipio_UF': 'Município'},
            color_discrete_sequence=COLOR_SCALE
        )
        fig_mun_puro.update_layout(
            hovermode='x unified',
            legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02)
        )
        st.plotly_chart(fig_mun_puro, width='stretch')
        
        # Gráfico de barras comparativo
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Total por Município")
            df_total_mun_puro = df_puro_filtrado.groupby('Municipio_UF')['Valor'].sum().reset_index().sort_values('Valor', ascending=False)
            
            fig_bar_mun_puro = px.bar(
                df_total_mun_puro,
                y='Municipio_UF',
                x='Valor',
                orientation='h',
                color='Municipio_UF',
                title=f"Total de Dados CMI_puro por Município",
                labels={'Valor': 'Total CMI_puro', 'Municipio_UF': 'Município'},
                color_discrete_sequence=COLOR_SCALE
            )
            fig_bar_mun_puro.update_layout(showlegend=False, yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig_bar_mun_puro, width='stretch')
        
        with col2:
            st.subheader("Média Anual")
            df_media_puro = df_puro_filtrado.groupby('Municipio_UF')['Valor'].mean().reset_index().sort_values('Valor', ascending=False)
            
            fig_media_puro = px.bar(
                df_media_puro,
                y='Municipio_UF',
                x='Valor',
                orientation='h',
                color='Municipio_UF',
                title="Média Anual por Município",
                labels={'Valor': 'Média Anual', 'Municipio_UF': 'Município'},
                color_discrete_sequence=COLOR_SCALE
            )
            fig_media_puro.update_layout(showlegend=False, yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig_media_puro, width='stretch')
        
        # Tabela de dados
        st.markdown("---")
        st.subheader("Dados Comparativos CMI_puro")
        
        df_resumo_mun_puro = df_puro_filtrado.groupby(['Municipio_UF', 'UF']).agg({
            'Valor': ['sum', 'mean', 'min', 'max']
        }).round(0)
        df_resumo_mun_puro.columns = ['Total', 'Média Anual', 'Mínimo', 'Máximo']
        df_resumo_mun_puro = df_resumo_mun_puro.sort_values('Total', ascending=False)
        
        st.dataframe(df_resumo_mun_puro, width='stretch')
        
        # Download
        csv = df_puro_filtrado.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="Baixar dados comparativos em CSV",
            data=csv,
            file_name=f"comparacao_municipios_CMI_puro_{anos_selecionados[0]}-{anos_selecionados[1]}.csv",
            mime="text/csv"
        )

# ===== MODO COMPARAÇÃO CMI =====
elif modo_visualizacao == "Comparação CMI":
    st.sidebar.markdown("---")
    
    # Verifica se há dados CMI_MIL e CMI_puro disponíveis
    ufs_cmi_mil_disponiveis = listar_ufs_cmi_disponiveis()
    ufs_cmi_puro_disponiveis = listar_ufs_cmi_puro_disponiveis()
    
    # Encontra UFs que existem em ambas as bases
    ufs_comuns = list(set(ufs_cmi_mil_disponiveis) & set(ufs_cmi_puro_disponiveis))
    
    if not ufs_comuns:
        st.warning("Nenhuma UF com dados CMI_MIL e CMI_puro encontrada!")
        st.info("Execute primeiro o script converter_dados.py para ambas as planilhas.")
        st.stop()
    
    # Tipo de comparação
    tipo_comparacao_cmi_comp = st.sidebar.radio(
        "Comparar por",
        ["Estados", "Municípios"],
        index=0
    )
    
    if tipo_comparacao_cmi_comp == "Estados":
        # Primeiro carrega dados de TODOS os estados para visão macro
        df_cmi_mil_todos = carregar_dados_multiplas_ufs(ufs_comuns, 'CMI_MIL')
        df_cmi_puro_todos = carregar_dados_multiplas_ufs(ufs_comuns, 'CMI_puro')
        
        if df_cmi_mil_todos is None or df_cmi_puro_todos is None:
            st.error("Erro ao carregar dados")
            st.stop()
        
        # Filtro de Anos (usa a intersecção dos anos disponíveis)
        anos_mil = set(df_cmi_mil_todos['Ano'].unique())
        anos_puro = set(df_cmi_puro_todos['Ano'].unique())
        anos_disponiveis = sorted(list(anos_mil & anos_puro))
        
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
        
        # Aplica filtros
        df_cmi_mil_filtrado_todos = df_cmi_mil_todos[
            (df_cmi_mil_todos['Ano'] >= anos_selecionados[0]) & 
            (df_cmi_mil_todos['Ano'] <= anos_selecionados[1])
        ]
        
        df_cmi_puro_filtrado_todos = df_cmi_puro_todos[
            (df_cmi_puro_todos['Ano'] >= anos_selecionados[0]) & 
            (df_cmi_puro_todos['Ano'] <= anos_selecionados[1])
        ]
        
        # ===== VISUALIZAÇÃO COMPARAÇÃO CMI_MIL vs CMI_puro =====
        st.title("📊 Comparação CMI_MIL vs CMI_puro")
        st.markdown("### Análise Comparativa dos Métodos de Cálculo do CMI")
        st.markdown("---")
        st.info("**CMI_MIL**: Método que analisa a cada mil óbitos regressivos, trazendo consistência aos dados. | **CMI_puro**: Método oficial do Ministério da Saúde.")
        
        # ===== VISÃO MACRO - BRASIL (TODOS OS ESTADOS) =====
        st.markdown("## 🇧🇷 Visão Nacional - Todos os Estados")
        st.markdown("#### Comparação Total Brasil: CMI_MIL vs CMI_puro")
        
        # Agrupa dados nacionais por ano
        df_mil_nacional = df_cmi_mil_filtrado_todos.groupby('Ano')['Valor'].sum().reset_index()
        df_puro_nacional = df_cmi_puro_filtrado_todos.groupby('Ano')['Valor'].sum().reset_index()
        
        # Combina os dados nacionais
        df_mil_nacional['Método'] = 'CMI_MIL'
        df_puro_nacional['Método'] = 'CMI_puro'
        df_nacional_combined = pd.concat([df_mil_nacional, df_puro_nacional])
        
        # Métricas nacionais
        total_mil_nacional = df_mil_nacional['Valor'].sum()
        total_puro_nacional = df_puro_nacional['Valor'].sum()
        diferenca_nacional = total_mil_nacional - total_puro_nacional
        perc_diferenca_nacional = (diferenca_nacional / total_puro_nacional * 100) if total_puro_nacional > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🔵 Total CMI_MIL (Brasil)", f"{total_mil_nacional:,.0f}".replace(",", "."))
        with col2:
            st.metric("🔴 Total CMI_puro (Brasil)", f"{total_puro_nacional:,.0f}".replace(",", "."))
        with col3:
            st.metric("Diferença Absoluta", f"{diferenca_nacional:,.0f}".replace(",", "."))
        with col4:
            st.metric("Diferença (%)", f"{perc_diferenca_nacional:+.2f}%")
        
        # Gráfico de linhas comparativo NACIONAL
        st.markdown("---")
        fig_nacional = px.line(
            df_nacional_combined,
            x='Ano',
            y='Valor',
            color='Método',
            title=f"Comparação Nacional CMI_MIL vs CMI_puro - Brasil ({anos_selecionados[0]}-{anos_selecionados[1]})",
            markers=True,
            labels={'Valor': 'Total Nacional', 'Método': 'Método'},
            color_discrete_map={'CMI_MIL': '#3b82f6', 'CMI_puro': '#ef4444'}
        )
        fig_nacional.update_layout(
            hovermode='x unified',
            height=500,
            font=dict(size=14)
        )
        fig_nacional.update_traces(line=dict(width=3))
        st.plotly_chart(fig_nacional, use_container_width=True)
        
        # Análise de Diferença Anual
        st.markdown("---")
        st.markdown("#### 📊 Análise da Diferença entre os Métodos por Ano")
        st.info("💡 **Como interpretar**: Valores positivos indicam que o CMI_MIL registrou mais casos que o CMI_puro. Valores negativos indicam o contrário.")
        
        # Calcula diferença por ano
        df_diferenca_ano = df_mil_nacional.copy()
        df_diferenca_ano['CMI_MIL'] = df_mil_nacional['Valor']
        df_diferenca_ano['CMI_puro'] = df_puro_nacional['Valor']
        df_diferenca_ano['Diferença'] = df_diferenca_ano['CMI_MIL'] - df_diferenca_ano['CMI_puro']
        df_diferenca_ano['Diferença %'] = ((df_diferenca_ano['CMI_MIL'] - df_diferenca_ano['CMI_puro']) / df_diferenca_ano['CMI_puro'] * 100)
        
        # Gráfico único combinado com cores significativas
        fig_diferenca_combinado = go.Figure()
        
        # Adiciona barras de diferença absoluta
        cores_barras = ['#22c55e' if x >= 0 else '#ef4444' for x in df_diferenca_ano['Diferença']]
        
        fig_diferenca_combinado.add_trace(go.Bar(
            x=df_diferenca_ano['Ano'],
            y=df_diferenca_ano['Diferença'],
            name='Diferença Absoluta',
            marker_color=cores_barras,
            text=df_diferenca_ano['Diferença'].round(0),
            textposition='outside',
            texttemplate='%{text:,.0f}',
            hovertemplate='<b>Ano %{x}</b><br>Diferença: %{y:,.0f}<br>CMI_MIL - CMI_puro<extra></extra>'
        ))
        
        # Adiciona linha de diferença percentual no eixo secundário
        fig_diferenca_combinado.add_trace(go.Scatter(
            x=df_diferenca_ano['Ano'],
            y=df_diferenca_ano['Diferença %'],
            name='Diferença %',
            yaxis='y2',
            mode='lines+markers',
            line=dict(color='#f59e0b', width=3),
            marker=dict(size=8, color='#f59e0b'),
            hovertemplate='<b>Ano %{x}</b><br>Diferença: %{y:.2f}%<extra></extra>'
        ))
        
        fig_diferenca_combinado.update_layout(
            title={
                'text': "Diferença entre CMI_MIL e CMI_puro por Ano<br><sub>Barras: Diferença Absoluta | Linha: Diferença Percentual</sub>",
                'x': 0.5,
                'xanchor': 'center'
            },
            xaxis=dict(title='Ano'),
            yaxis=dict(
                title='Diferença Absoluta (CMI_MIL - CMI_puro)',
                titlefont=dict(color='#1f2937'),
                tickfont=dict(color='#1f2937')
            ),
            yaxis2=dict(
                title='Diferença Percentual (%)',
                titlefont=dict(color='#f59e0b'),
                tickfont=dict(color='#f59e0b'),
                overlaying='y',
                side='right'
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            hovermode='x unified',
            height=500
        )
        
        st.plotly_chart(fig_diferenca_combinado, use_container_width=True)
        
        # Explicação adicional
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**🟢 Verde**: CMI_MIL registrou mais casos")
            st.markdown("**🔴 Vermelho**: CMI_puro registrou mais casos")
        with col2:
            st.markdown("**📊 Barras**: Diferença em números absolutos")
            st.markdown("**📈 Linha Laranja**: Diferença em porcentagem")
        
        # Tabela de dados detalhados
        with st.expander("📋 Ver Tabela Detalhada Nacional"):
            df_tabela_nacional = df_diferenca_ano[['Ano', 'CMI_MIL', 'CMI_puro', 'Diferença', 'Diferença %']].copy()
            df_tabela_nacional.columns = ['Ano', 'CMI_MIL', 'CMI_puro', 'Diferença', 'Diferença (%)']
            df_tabela_nacional = df_tabela_nacional.round(2)
            st.dataframe(df_tabela_nacional, use_container_width=True)
        
        st.markdown("---")
        st.markdown("## 📍 Análise por Estado Individual")
        st.markdown("Selecione estados específicos para análise detalhada:")
        
        # Agora permite selecionar estados específicos para análise detalhada
        ufs_comparacao_selecionadas = st.multiselect(
            "Estados para Análise Detalhada (opcional)",
            ufs_comuns,
            default=[]
        )
        
        # Gráfico de comparação por estado (se selecionados)
        # Gráfico de comparação por estado (se selecionados)
        if ufs_comparacao_selecionadas:
            for uf in ufs_comparacao_selecionadas:
                st.markdown(f"### Estado: {uf}")
                
                # Dados por ano para esta UF
                df_mil_uf = df_cmi_mil_filtrado_todos[df_cmi_mil_filtrado_todos['UF'] == uf].groupby('Ano')['Valor'].sum().reset_index()
                df_puro_uf = df_cmi_puro_filtrado_todos[df_cmi_puro_filtrado_todos['UF'] == uf].groupby('Ano')['Valor'].sum().reset_index()
                
                # Combina os dados
                df_mil_uf['Método'] = 'CMI_MIL'
                df_puro_uf['Método'] = 'CMI_puro'
                df_combined = pd.concat([df_mil_uf, df_puro_uf])
                
                # Gráfico de linhas comparativo
                fig_comp = px.line(
                    df_combined,
                    x='Ano',
                    y='Valor',
                    color='Método',
                    title=f"Comparação CMI_MIL vs CMI_puro - {uf}",
                    markers=True,
                    labels={'Valor': 'Total', 'Método': 'Método'},
                    color_discrete_map={'CMI_MIL': '#3b82f6', 'CMI_puro': '#ef4444'}
                )
                fig_comp.update_layout(hovermode='x unified')
                st.plotly_chart(fig_comp, use_container_width=True)
                
                # Métricas comparativas
                col1, col2, col3 = st.columns(3)
                
                total_mil = df_mil_uf['Valor'].sum()
                total_puro = df_puro_uf['Valor'].sum()
                diferenca = total_mil - total_puro
                perc_diferenca = (diferenca / total_puro * 100) if total_puro > 0 else 0
                
                with col1:
                    st.metric("Total CMI_MIL", f"{total_mil:,.0f}".replace(",", "."))
                with col2:
                    st.metric("Total CMI_puro", f"{total_puro:,.0f}".replace(",", "."))
                with col3:
                    st.metric("Diferença (%)", f"{perc_diferenca:+.2f}%")
                
                st.markdown("---")
        else:
            st.info("👆 Selecione estados acima para ver análises individuais detalhadas.")
        
    else:  # Comparação por Municípios
        # Primeiro seleciona estados
        ufs_para_municipios_comp = st.sidebar.multiselect(
            "Estados (para listar municípios)",
            ufs_comuns,
            default=ufs_comuns[:1] if len(ufs_comuns) >= 1 else ufs_comuns
        )
        
        if not ufs_para_municipios_comp:
            st.warning("Selecione pelo menos um estado")
            st.stop()
        
        # Carrega dados
        df_mil_temp = carregar_dados_multiplas_ufs(ufs_para_municipios_comp, 'CMI_MIL')
        df_puro_temp = carregar_dados_multiplas_ufs(ufs_para_municipios_comp, 'CMI_puro')
        
        if df_mil_temp is None or df_puro_temp is None:
            st.error("Erro ao carregar dados")
            st.stop()
        
        # Lista municípios que existem em ambas as bases
        municipios_mil = set(df_mil_temp['Municipio'])
        municipios_puro = set(df_puro_temp['Municipio'])
        municipios_comuns = sorted(list(municipios_mil & municipios_puro))
        
        if not municipios_comuns:
            st.warning("Nenhum município em comum encontrado")
            st.stop()
        
        # Seleciona municípios
        municipios_comp_selecionados = st.sidebar.multiselect(
            "Selecione os Municípios para Comparar",
            municipios_comuns,
            default=municipios_comuns[:3] if len(municipios_comuns) >= 3 else municipios_comuns
        )
        
        if not municipios_comp_selecionados:
            st.warning("Selecione pelo menos um município")
            st.stop()
        
        # Filtro de Anos
        anos_mil = set(df_mil_temp['Ano'].unique())
        anos_puro = set(df_puro_temp['Ano'].unique())
        anos_disponiveis = sorted(list(anos_mil & anos_puro))
        
        if not anos_disponiveis:
            st.error("Nenhum ano em comum entre as bases")
            st.stop()
        
        ano_min = int(min(anos_disponiveis))
        ano_max = int(max(anos_disponiveis))
        
        anos_selecionados = st.sidebar.slider(
            "Período",
            ano_min,
            ano_max,
            (ano_min, ano_max)
        )
        
        # Filtra dados
        df_mil_filtrado_todos = df_mil_temp[
            (df_mil_temp['Ano'] >= anos_selecionados[0]) & 
            (df_mil_temp['Ano'] <= anos_selecionados[1])
        ]
        
        df_puro_filtrado_todos = df_puro_temp[
            (df_puro_temp['Ano'] >= anos_selecionados[0]) & 
            (df_puro_temp['Ano'] <= anos_selecionados[1])
        ]
        
        # ===== VISUALIZAÇÃO COMPARAÇÃO POR MUNICÍPIOS =====
        st.title("📊 Comparação CMI_MIL vs CMI_puro por Município")
        st.markdown("### Análise Comparativa dos Métodos de Cálculo do CMI")
        st.markdown("---")
        st.info("**CMI_MIL**: Método que analisa a cada mil óbitos regressivos, trazendo consistência aos dados. | **CMI_puro**: Método oficial do Ministério da Saúde.")
        
        # ===== VISÃO MACRO - TOTAL DOS ESTADOS SELECIONADOS =====
        st.markdown(f"## 🌍 Visão Consolidada - {len(ufs_para_municipios_comp)} Estado(s)")
        st.markdown(f"#### Comparação Total: CMI_MIL vs CMI_puro (Estados: {', '.join(ufs_para_municipios_comp)})")
        
        # Agrupa dados consolidados por ano
        df_mil_consolidado = df_mil_filtrado_todos.groupby('Ano')['Valor'].sum().reset_index()
        df_puro_consolidado = df_puro_filtrado_todos.groupby('Ano')['Valor'].sum().reset_index()
        
        # Combina os dados consolidados
        df_mil_consolidado['Método'] = 'CMI_MIL'
        df_puro_consolidado['Método'] = 'CMI_puro'
        df_consolidado_combined = pd.concat([df_mil_consolidado, df_puro_consolidado])
        
        # Métricas consolidadas
        total_mil_consolidado = df_mil_consolidado['Valor'].sum()
        total_puro_consolidado = df_puro_consolidado['Valor'].sum()
        diferenca_consolidado = total_mil_consolidado - total_puro_consolidado
        perc_diferenca_consolidado = (diferenca_consolidado / total_puro_consolidado * 100) if total_puro_consolidado > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🔵 Total CMI_MIL", f"{total_mil_consolidado:,.0f}".replace(",", "."))
        with col2:
            st.metric("🔴 Total CMI_puro", f"{total_puro_consolidado:,.0f}".replace(",", "."))
        with col3:
            st.metric("Diferença Absoluta", f"{diferenca_consolidado:,.0f}".replace(",", "."))
        with col4:
            st.metric("Diferença (%)", f"{perc_diferenca_consolidado:+.2f}%")
        
        # Gráfico de linhas comparativo CONSOLIDADO
        st.markdown("---")
        fig_consolidado = px.line(
            df_consolidado_combined,
            x='Ano',
            y='Valor',
            color='Método',
            title=f"Comparação Consolidada CMI_MIL vs CMI_puro ({anos_selecionados[0]}-{anos_selecionados[1]})",
            markers=True,
            labels={'Valor': 'Total', 'Método': 'Método'},
            color_discrete_map={'CMI_MIL': '#3b82f6', 'CMI_puro': '#ef4444'}
        )
        fig_consolidado.update_layout(
            hovermode='x unified',
            height=500,
            font=dict(size=14)
        )
        fig_consolidado.update_traces(line=dict(width=3))
        st.plotly_chart(fig_consolidado, use_container_width=True)
        
        st.markdown("---")
        st.markdown("## 📍 Análise por Município Individual")
        st.markdown("Selecione municípios específicos para análise detalhada:")
        
        # Agora permite selecionar municípios específicos para análise detalhada
        municipios_comp_selecionados = st.multiselect(
            "Municípios para Análise Detalhada (opcional)",
            municipios_comuns,
            default=[]
        )
        
        # Filtra dados por município
        df_mil_filtrado = df_mil_temp[
            (df_mil_temp['Municipio'].isin(municipios_comp_selecionados)) &
            (df_mil_temp['Ano'] >= anos_selecionados[0]) & 
            (df_mil_temp['Ano'] <= anos_selecionados[1])
        ]
        
        df_puro_filtrado = df_puro_temp[
            (df_puro_temp['Municipio'].isin(municipios_comp_selecionados)) &
            (df_puro_temp['Ano'] >= anos_selecionados[0]) & 
            (df_puro_temp['Ano'] <= anos_selecionados[1])
        ]
        
        # Gráfico comparativo para cada município (se selecionados)
        if municipios_comp_selecionados:
            for municipio in municipios_comp_selecionados:
                st.markdown(f"### Município: {municipio}")
                
                # Dados por ano para este município
                df_mil_mun = df_mil_filtrado[df_mil_filtrado['Municipio'] == municipio].groupby('Ano')['Valor'].sum().reset_index()
                df_puro_mun = df_puro_filtrado[df_puro_filtrado['Municipio'] == municipio].groupby('Ano')['Valor'].sum().reset_index()
                
                # Combina os dados
                df_mil_mun['Método'] = 'CMI_MIL'
                df_puro_mun['Método'] = 'CMI_puro'
                df_combined_mun = pd.concat([df_mil_mun, df_puro_mun])
                
                # Gráfico de linhas comparativo
                fig_comp_mun = px.line(
                    df_combined_mun,
                    x='Ano',
                    y='Valor',
                    color='Método',
                    title=f"Comparação CMI_MIL vs CMI_puro - {municipio}",
                    markers=True,
                    labels={'Valor': 'Total', 'Método': 'Método'},
                    color_discrete_map={'CMI_MIL': '#3b82f6', 'CMI_puro': '#ef4444'}
                )
                fig_comp_mun.update_layout(hovermode='x unified')
                st.plotly_chart(fig_comp_mun, use_container_width=True)
                
                # Métricas comparativas
                col1, col2, col3 = st.columns(3)
                
                total_mil_mun = df_mil_mun['Valor'].sum()
                total_puro_mun = df_puro_mun['Valor'].sum()
                diferenca_mun = total_mil_mun - total_puro_mun
                perc_diferenca_mun = (diferenca_mun / total_puro_mun * 100) if total_puro_mun > 0 else 0
                
                with col1:
                    st.metric("Total CMI_MIL", f"{total_mil_mun:,.0f}".replace(",", "."))
                with col2:
                    st.metric("Total CMI_puro", f"{total_puro_mun:,.0f}".replace(",", "."))
                with col3:
                    st.metric("Diferença (%)", f"{perc_diferenca_mun:+.2f}%")
                
                st.markdown("---")
        else:
            st.info("👆 Selecione municípios acima para ver análises individuais detalhadas.")

# ===== MODO ESTADO INDIVIDUAL =====
else:
    # Filtro de UF
    uf_selecionada = st.sidebar.selectbox(
        "Selecione o Estado (UF)",
        ufs_disponiveis,
        index=0
    )

    # Filtro de tipo de dado
    tipo_dado = st.sidebar.radio(
        "Tipo de Dado",
        ["Nascidos Vivos", "Óbitos"],
        index=0
    )

    tipo_cod = 'NV' if tipo_dado == "Nascidos Vivos" else 'OB'

    # Carrega dados
    df = carregar_dados_uf(uf_selecionada, tipo_cod)

    if df is None or len(df) == 0:
        st.error(f"Não há dados de {tipo_dado} para {uf_selecionada}")
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

    # Filtro de Municípios
    municipios_disponiveis = sorted(df['Municipio'].unique())
    municipios_selecionados = st.sidebar.multiselect(
        "Selecione Municípios (deixe vazio para todos)",
        municipios_disponiveis,
        default=[]
    )

    # Aplica filtros
    df_filtrado = df[
        (df['Ano'] >= anos_selecionados[0]) & 
        (df['Ano'] <= anos_selecionados[1])
    ]

    if municipios_selecionados:
        df_filtrado = df_filtrado[df_filtrado['Municipio'].isin(municipios_selecionados)]

    # ===== MÉTRICAS PRINCIPAIS =====
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)

    # Calcula totais
    total_geral = df_filtrado['Valor'].sum()
    total_ano_atual = df_filtrado[df_filtrado['Ano'] == anos_selecionados[1]]['Valor'].sum()
    media_anual = df_filtrado.groupby('Ano')['Valor'].sum().mean()
    num_municipios = df_filtrado['Municipio'].nunique()

    with col1:
        st.metric(
            "Total no Período",
            f"{total_geral:,.0f}".replace(",", ".")
        )

    with col2:
        st.metric(
            f"Total em {anos_selecionados[1]}",
            f"{total_ano_atual:,.0f}".replace(",", ".")
        )

    with col3:
        st.metric(
            "Média Anual",
            f"{media_anual:,.0f}".replace(",", ".")
        )

    with col4:
        st.metric(
            "Municípios",
            f"{num_municipios}"
        )

    # ===== GRÁFICOS =====
    st.markdown("---")

    # Aba de visualizações
    tab1, tab2, tab3, tab4 = st.tabs([
        "Evolução Temporal",
        "Por Município",
        "Ranking",
        "Dados Brutos"
    ])

    with tab1:
        st.subheader(f"Evolução de {tipo_dado} ao Longo do Tempo")
        
        # Agrupa por ano
        df_por_ano = df_filtrado.groupby('Ano')['Valor'].sum().reset_index()
        
        # Gráfico de linha
        fig = px.line(
            df_por_ano,
            x='Ano',
            y='Valor',
            title=f"Total de {tipo_dado} por Ano - {uf_selecionada}",
            markers=True
        )
        fig.update_layout(
            xaxis_title="Ano",
            yaxis_title=f"Total de {tipo_dado}",
            hovermode='x'
        )
        st.plotly_chart(fig, width='stretch')
        
        # Se municípios selecionados, mostra comparação
        if municipios_selecionados and len(municipios_selecionados) <= 10:
            st.markdown("### Comparação entre Municípios Selecionados")
            df_comp = df_filtrado.groupby(['Ano', 'Municipio'])['Valor'].sum().reset_index()
            
            fig2 = px.line(
                df_comp,
                x='Ano',
                y='Valor',
                color='Municipio',
                title=f"Comparação de {tipo_dado} entre Municípios",
                markers=True
            )
            st.plotly_chart(fig2, width='stretch')

    with tab2:
        st.subheader(f"Distribuição de {tipo_dado} por Município")
        
        # Agrupa por município
        df_por_municipio = df_filtrado.groupby('Municipio')['Valor'].sum().reset_index()
        df_por_municipio = df_por_municipio.sort_values('Valor', ascending=False)
        
        # Gráfico de barras (top 20)
        top_n = 20 if not municipios_selecionados else len(municipios_selecionados)
        df_top = df_por_municipio.head(top_n)
        
        fig3 = px.bar(
            df_top,
            y='Municipio',
            x='Valor',
            orientation='h',
            title=f"Top {top_n} Municípios - Total de {tipo_dado} ({anos_selecionados[0]}-{anos_selecionados[1]})",
            labels={'Valor': f'Total de {tipo_dado}', 'Municipio': 'Município'}
        )
        fig3.update_layout(height=600, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig3, width='stretch')

    with tab3:
        st.subheader(f"Ranking de Municípios")
        
        col_rank1, col_rank2 = st.columns(2)
        
        with col_rank1:
            st.markdown("#### Top 10 Municípios")
            df_rank_top = df_por_municipio.head(10).reset_index(drop=True)
            df_rank_top.index += 1
            df_rank_top.columns = ['Município', f'Total {tipo_dado}']
            st.dataframe(df_rank_top, width='stretch')
        
        with col_rank2:
            st.markdown("#### Estatísticas Gerais")
            estatisticas = df_por_municipio['Valor'].describe()
            st.write(f"**Média:** {estatisticas['mean']:,.0f}".replace(",", "."))
            st.write(f"**Mediana:** {estatisticas['50%']:,.0f}".replace(",", "."))
            st.write(f"**Desvio Padrão:** {estatisticas['std']:,.0f}".replace(",", "."))
            st.write(f"**Mínimo:** {estatisticas['min']:,.0f}".replace(",", "."))
            st.write(f"**Máximo:** {estatisticas['max']:,.0f}".replace(",", "."))

    with tab4:
        st.subheader("Dados Brutos")
        
        # Opções de visualização
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            ordem = st.selectbox(
                "Ordenar por",
                ['Ano', 'Municipio', 'Valor']
            )
        with col_d2:
            crescente = st.checkbox("Ordem Crescente", value=False)
        
        df_display = df_filtrado.sort_values(ordem, ascending=crescente)
        df_display = df_display.rename(columns={
            'Municipio': 'Município',
            'Valor': tipo_dado,
            'Ano': 'Ano',
            'UF': 'UF',
            'Tipo': 'Tipo'
        })
        
        st.dataframe(df_display, width='stretch', height=400)
        
        # Botão de download
        csv = df_display.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="Baixar dados em CSV",
            data=csv,
            file_name=f"dados_{uf_selecionada}_{tipo_cod}_{anos_selecionados[0]}-{anos_selecionados[1]}.csv",
            mime="text/csv"
        )

    # Rodapé
    st.markdown("---")
    st.markdown(f"**Fonte:** Dados.xlsx | **Total de registros exibidos:** {len(df_filtrado):,}".replace(",", "."))
