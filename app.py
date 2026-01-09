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

# Caminhos
BASE_DIR = Path(__file__).parent  # app.py está na raiz
DIR_NV = BASE_DIR / 'data' / 'output' / 'nascidos_vivos'
DIR_OB = BASE_DIR / 'data' / 'output' / 'obitos'

# Cache dos dados
@st.cache_data
def carregar_dados_uf(uf, tipo):
    """
    Carrega dados de uma UF específica (NV ou OB)
    """
    diretorio = DIR_NV if tipo == 'NV' else DIR_OB
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
st.title("Dashboard de Saúde Pública")
st.markdown("### Análise de Nascidos Vivos e Óbitos por Município e Estado")

# Sidebar
st.sidebar.header("Filtros")

# Modo de visualização
modo_visualizacao = st.sidebar.radio(
    "Modo de Visualização",
    ["Estado Individual", "Comparação"],
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
            labels={'Valor': f'Total de {tipo_dado}', 'UF': 'Estado'}
        )
        fig_estados.update_layout(
            hovermode='x unified',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
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
                labels={'Valor': f'Total de {tipo_dado}', 'UF': 'Estado'}
            )
            st.plotly_chart(fig_bar, width='stretch')
        
        with col2:
            st.subheader("Distribuição Percentual")
            fig_pie = px.pie(
                df_total_estados,
                values='Valor',
                names='UF',
                title=f"Participação de cada Estado"
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
