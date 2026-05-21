#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APP3 - Dashboard Streamlit para Análise de CMI e CMI-Mil

Modos:
1. CMI-MIL: Visualização individual do CMI-Mil (municípios)
2. CMI (Comparação): Comparação entre CMI e CMI-Mil no mesmo gráfico (municípios)

Dados:
- CMI: data/output/cmi_app3/
- CMI-Mil: data/output/cmi-mil_app3/
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from pathlib import Path

# Configuração da página
st.set_page_config(
    page_title="APP3 - CMI & CMI-Mil",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Diretórios de dados
BASE_DIR = Path(__file__).parent
DIR_CMI = BASE_DIR / 'data' / 'output' / 'cmi_app3'
DIR_CMI_MIL = BASE_DIR / 'data' / 'output' / 'cmi-mil_app3'

# Paleta de cores
COLOR_CMI = '#ef4444'  # Vermelho
COLOR_CMI_MIL = '#3b82f6'  # Azul

# ===== FUNÇÕES AUXILIARES =====

@st.cache_data(ttl=60)  # Cache expira após 60 segundos
def carregar_todos_dados(diretorio):
    """Carrega todos os JSONs de um diretório em um único DataFrame"""
    todos_registros = []
    
    for arquivo in diretorio.glob('*.json'):
        try:
            with open(arquivo, 'r', encoding='utf-8') as f:
                registros = json.load(f)
                todos_registros.extend(registros)
        except Exception as e:
            st.error(f"Erro ao carregar {arquivo.name}: {e}")
    
    if todos_registros:
        df = pd.DataFrame(todos_registros)
        # Cria coluna combinada Município + UF
        df['Municipio_UF'] = df['Municipio'] + ' - ' + df['UF']
        return df
    
    return None


def listar_municipios_disponiveis(df):
    """Lista todos os municípios disponíveis (com código)"""
    if df is None:
        return []
    
    municipios = df.groupby(['Municipio_UF', 'Codigo_Municipio']).size().reset_index()[['Municipio_UF', 'Codigo_Municipio']]
    municipios_list = []
    
    for _, row in municipios.iterrows():
        codigo = row['Codigo_Municipio']
        nome_uf = row['Municipio_UF']
        
        if codigo:
            municipios_list.append(f"{codigo} {nome_uf}")
        else:
            municipios_list.append(nome_uf)
    
    return sorted(municipios_list)


# ===== CARREGAMENTO DE DADOS =====

st.title("📊 APP3 - Análise CMI & CMI-Mil")
st.markdown("### Dashboard para Visualização de Coeficientes de Mortalidade Infantil")
st.markdown("---")

# Carrega todos os dados
df_cmi = carregar_todos_dados(DIR_CMI)
df_cmi_mil = carregar_todos_dados(DIR_CMI_MIL)

if df_cmi is None and df_cmi_mil is None:
    st.error("❌ Nenhum dado encontrado! Execute primeiro o script raspagem_app3.py")
    st.stop()

# ===== SIDEBAR =====

st.sidebar.title("⚙️ Configurações")

# Botão para limpar cache
if st.sidebar.button("🔄 Recarregar Dados", help="Limpa o cache e recarrega os dados dos arquivos JSON"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")

# Seleção do modo
modo = st.sidebar.radio(
    "Modo de Visualização",
    ["CMI-Mil", "CMI (Comparação)"],
    help="CMI-Mil: Apenas CMI-Mil | CMI: Comparação CMI vs CMI-Mil"
)

st.sidebar.markdown("---")

# ===== SELEÇÃO DE MUNICÍPIOS (COMUM PARA AMBOS OS MODOS) =====

st.sidebar.markdown("### 📍 Seleção de Municípios")

# Define lista de municípios disponíveis baseado no modo
if modo == "CMI-Mil":
    st.sidebar.info("Modo: Apenas CMI-Mil (metodologia factual)")
    
    if df_cmi_mil is None:
        st.error("❌ Dados de CMI-Mil não encontrados!")
        st.stop()
    
    # Lista municípios disponíveis (sem código, apenas nome - UF)
    municipios_disponiveis = sorted(df_cmi_mil['Municipio_UF'].unique())
    
else:  # CMI (Comparação)
    st.sidebar.info("Modo: Comparação CMI vs CMI-Mil")
    
    if df_cmi is None or df_cmi_mil is None:
        st.error("❌ Dados de CMI ou CMI-Mil não encontrados!")
        st.stop()
    
    # Municípios que existem em AMBAS as bases
    municipios_cmi = set(df_cmi['Municipio_UF'].unique())
    municipios_mil = set(df_cmi_mil['Municipio_UF'].unique())
    municipios_disponiveis = sorted(list(municipios_cmi & municipios_mil))

if not municipios_disponiveis:
    st.error("❌ Nenhum município encontrado")
    st.stop()

# Seleção de municípios (mantém a seleção entre modos usando key única)
municipios_selecionados = st.sidebar.multiselect(
    "Selecione os Municípios",
    municipios_disponiveis,
    default=[],
    key="municipios_selecionados",
    help="Você pode selecionar múltiplos municípios para comparação"
)

st.sidebar.markdown("---")

# ===== MODO CMI-MIL (SOZINHO) =====

if modo == "CMI-Mil":
    
    if not municipios_selecionados:
        st.warning("👆 Selecione pelo menos um município na barra lateral")
        
        # Mostra estatísticas gerais
        st.markdown("## 📊 Estatísticas Gerais - CMI-Mil")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total de Registros", f"{len(df_cmi_mil):,}")
        
        with col2:
            st.metric("Estados", df_cmi_mil['UF'].nunique())
        
        with col3:
            st.metric("Municípios", df_cmi_mil['Municipio'].nunique())
        
        with col4:
            anos = df_cmi_mil['Ano'].unique()
            st.metric("Período", f"{min(anos)} - {max(anos)}")
        
        st.stop()
    
    # Filtra dados diretamente usando Municipio_UF
    df_filtrado = df_cmi_mil[df_cmi_mil['Municipio_UF'].isin(municipios_selecionados)]
    
    if df_filtrado.empty:
        st.error("❌ Nenhum dado encontrado para os municípios selecionados")
        st.stop()
    
    # Filtro de anos
    anos_disponiveis = sorted(df_filtrado['Ano'].unique())
    
    if len(anos_disponiveis) > 1:
        ano_min = int(min(anos_disponiveis))
        ano_max = int(max(anos_disponiveis))
        
        anos_selecionados = st.sidebar.slider(
            "Período",
            ano_min,
            ano_max,
            (ano_min, ano_max)
        )
        
        df_filtrado = df_filtrado[
            (df_filtrado['Ano'] >= anos_selecionados[0]) &
            (df_filtrado['Ano'] <= anos_selecionados[1])
        ]
    
    # ===== VISUALIZAÇÃO CMI-MIL =====
    
    st.markdown(f"## 📈 CMI-Mil - {len(municipios_selecionados)} Município(s) Selecionado(s)")
    st.info("""
    **CMI-Mil (Metodologia Factual)**: Acumula óbitos até chegar em 1000, então calcula o coeficiente.
    Proporciona uma análise mais estável baseada em fatos, não em pré-suposições.
    """)
    
    # Métricas
    st.markdown("### 📊 Métricas")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        media_geral = df_filtrado['Valor'].mean()
        st.metric("CMI-Mil Médio", f"{media_geral:.2f} ‰")
    
    with col2:
        valor_max = df_filtrado['Valor'].max()
        st.metric("Valor Máximo", f"{valor_max:.2f} ‰")
    
    with col3:
        valor_min = df_filtrado['Valor'].min()
        st.metric("Valor Mínimo", f"{valor_min:.2f} ‰")
    
    # Gráfico de linha
    st.markdown("---")
    st.markdown("### 📈 Evolução Temporal")
    
    fig = px.line(
        df_filtrado,
        x='Ano',
        y='Valor',
        color='Municipio_UF',
        title=f"CMI-Mil por Ano - {len(municipios_selecionados)} Município(s)",
        markers=True,
        labels={'Valor': 'CMI-Mil (por 1000)', 'Municipio_UF': 'Município'},
        color_discrete_sequence=[COLOR_CMI_MIL]
    )
    
    fig.update_layout(
        height=600,
        hovermode='x unified',
        xaxis_title="Ano",
        yaxis_title="CMI-Mil (‰)"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Tabela de dados
    st.markdown("---")
    st.markdown("### 📋 Dados Detalhados")
    
    df_display = df_filtrado[['Municipio', 'UF', 'Ano', 'Valor', 'Codigo_Municipio']].sort_values(['Municipio', 'Ano'])
    df_display = df_display.rename(columns={
        'Municipio': 'Município',
        'Valor': 'CMI-Mil',
        'Codigo_Municipio': 'Código'
    })
    
    st.dataframe(df_display, use_container_width=True, height=400)


# ===== MODO CMI (COMPARAÇÃO) =====

elif modo == "CMI (Comparação)":
    
    if not municipios_selecionados:
        st.warning("👆 Selecione pelo menos um município na barra lateral para comparação")
        
        # Mostra estatísticas
        st.markdown("## 📊 Estatísticas Gerais")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### CMI (Tradicional)")
            st.metric("Total de Registros", f"{len(df_cmi):,}")
            st.metric("Municípios", df_cmi['Municipio'].nunique())
        
        with col2:
            st.markdown("### CMI-Mil (Factual)")
            st.metric("Total de Registros", f"{len(df_cmi_mil):,}")
            st.metric("Municípios", df_cmi_mil['Municipio'].nunique())
        
        # Calcula municípios em comum
        municipios_cmi = set(df_cmi['Municipio_UF'].unique())
        municipios_mil = set(df_cmi_mil['Municipio_UF'].unique())
        municipios_comuns = municipios_cmi & municipios_mil
        
        st.info(f"💡 {len(municipios_comuns)} municípios disponíveis para comparação")
        
        st.stop()
    
    # Filtra dados de ambas as bases
    df_cmi_filtrado = df_cmi[df_cmi['Municipio_UF'].isin(municipios_selecionados)]
    df_mil_filtrado = df_cmi_mil[df_cmi_mil['Municipio_UF'].isin(municipios_selecionados)]
    
    if df_cmi_filtrado.empty and df_mil_filtrado.empty:
        st.error("❌ Nenhum dado encontrado para os municípios selecionados")
        st.stop()
    
    # Filtro de anos (usa a união dos anos disponíveis)
    anos_cmi = set(df_cmi_filtrado['Ano'].unique())
    anos_mil = set(df_mil_filtrado['Ano'].unique())
    anos_todos = sorted(list(anos_cmi | anos_mil))
    
    if len(anos_todos) > 1:
        ano_min = int(min(anos_todos))
        ano_max = int(max(anos_todos))
        
        anos_selecionados = st.sidebar.slider(
            "Período",
            ano_min,
            ano_max,
            (ano_min, ano_max)
        )
        
        df_cmi_filtrado = df_cmi_filtrado[
            (df_cmi_filtrado['Ano'] >= anos_selecionados[0]) &
            (df_cmi_filtrado['Ano'] <= anos_selecionados[1])
        ]
        
        df_mil_filtrado = df_mil_filtrado[
            (df_mil_filtrado['Ano'] >= anos_selecionados[0]) &
            (df_mil_filtrado['Ano'] <= anos_selecionados[1])
        ]
    
    # ===== VISUALIZAÇÃO COMPARATIVA =====
    
    st.markdown(f"## 📊 Comparação CMI vs CMI-Mil - {len(municipios_selecionados)} Município(s)")
    st.info("""
    **CMI (Tradicional)**: Cálculo por regra de 3 - (Óbitos × 1000) / Nascidos Vivos. Mais variável.
    
    **CMI-Mil (Factual)**: Acumula óbitos até 1000, depois calcula. Mais estável e baseado em fatos.
    """)
    
    # Se múltiplos municípios: mostra CMI-Mil grande no topo com linhas suavizadas
    if len(municipios_selecionados) > 1 and not df_mil_filtrado.empty:
        st.markdown("### 📈 CMI-Mil - Visão Geral (Linhas Suavizadas)")
        
        fig_mil_top = px.line(
            df_mil_filtrado,
            x='Ano',
            y='Valor',
            color='Municipio_UF',
            title=f"CMI-Mil - {len(municipios_selecionados)} Municípios",
            markers=True,
            labels={'Valor': 'CMI-Mil (‰)', 'Municipio_UF': 'Município'},
            line_shape='spline'  # Linhas suavizadas para diferenciar do gráfico de baixo
        )
        
        fig_mil_top.update_layout(
            height=500,
            hovermode='x unified',
            xaxis_title="Ano",
            yaxis_title="CMI-Mil (‰)",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        st.plotly_chart(fig_mil_top, use_container_width=True)
        
        st.markdown("---")
    
    # Gráficos lado a lado: CMI e CMI-Mil
    st.markdown("### 📈 Comparação Temporal")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**CMI (Tradicional)**")
        
        # Métricas CMI
        if not df_cmi_filtrado.empty:
            col1a, col1b, col1c = st.columns(3)
            
            with col1a:
                media_cmi = df_cmi_filtrado['Valor'].mean()
                st.metric("Média", f"{media_cmi:.2f} ‰")
            
            with col1b:
                max_cmi = df_cmi_filtrado['Valor'].max()
                st.metric("Máximo", f"{max_cmi:.2f} ‰")
            
            with col1c:
                min_cmi = df_cmi_filtrado['Valor'].min()
                st.metric("Mínimo", f"{min_cmi:.2f} ‰")
            
            # Gráfico CMI
            fig_cmi = px.line(
                df_cmi_filtrado,
                x='Ano',
                y='Valor',
                color='Municipio_UF',
                markers=True,
                labels={'Valor': 'CMI (‰)', 'Municipio_UF': 'Município'},
                color_discrete_sequence=[COLOR_CMI]
            )
            
            fig_cmi.update_layout(
                height=450,
                hovermode='x unified',
                xaxis_title="Ano",
                yaxis_title="CMI (‰)",
                showlegend=(len(municipios_selecionados) > 1)
            )
            
            st.plotly_chart(fig_cmi, use_container_width=True)
        else:
            st.info("Sem dados CMI para o período")
    
    with col2:
        st.markdown("**CMI-Mil (Factual)**")
        
        # Métricas CMI-Mil
        if not df_mil_filtrado.empty:
            col2a, col2b, col2c = st.columns(3)
            
            with col2a:
                media_mil = df_mil_filtrado['Valor'].mean()
                st.metric("Média", f"{media_mil:.2f} ‰")
            
            with col2b:
                max_mil = df_mil_filtrado['Valor'].max()
                st.metric("Máximo", f"{max_mil:.2f} ‰")
            
            with col2c:
                min_mil = df_mil_filtrado['Valor'].min()
                st.metric("Mínimo", f"{min_mil:.2f} ‰")
            
            # Gráfico CMI-Mil
            fig_mil = px.line(
                df_mil_filtrado,
                x='Ano',
                y='Valor',
                color='Municipio_UF',
                markers=True,
                labels={'Valor': 'CMI-Mil (‰)', 'Municipio_UF': 'Município'},
                color_discrete_sequence=[COLOR_CMI_MIL]
            )
            
            fig_mil.update_layout(
                height=450,
                hovermode='x unified',
                xaxis_title="Ano",
                yaxis_title="CMI-Mil (‰)",
                showlegend=(len(municipios_selecionados) > 1)
            )
            
            st.plotly_chart(fig_mil, use_container_width=True)
        else:
            st.info("Sem dados CMI-Mil para o período")
    
    # Estatísticas gerais
    st.markdown("---")
    st.markdown("### 📊 Estatísticas Gerais")
    
    col1, col2 = st.columns(2)
    
    with col1:
        anos_cmi_count = len(df_cmi_filtrado['Ano'].unique()) if not df_cmi_filtrado.empty else 0
        st.metric("Anos CMI", anos_cmi_count)
    
    with col2:
        anos_mil_count = len(df_mil_filtrado['Ano'].unique()) if not df_mil_filtrado.empty else 0
        st.metric("Anos CMI-Mil", anos_mil_count)
    
    # Análise detalhada por município
    st.markdown("---")
    st.markdown("### 📋 Análise por Município")
    
    for municipio in municipios_selecionados:
        with st.expander(f"📍 {municipio}"):
            df_mun_cmi = df_cmi_filtrado[df_cmi_filtrado['Municipio_UF'] == municipio]
            df_mun_mil = df_mil_filtrado[df_mil_filtrado['Municipio_UF'] == municipio]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**CMI (Tradicional)**")
                if not df_mun_cmi.empty:
                    st.write(f"Período: {df_mun_cmi['Ano'].min()} - {df_mun_cmi['Ano'].max()}")
                    st.write(f"Média: {df_mun_cmi['Valor'].mean():.2f} ‰")
                    st.write(f"Registros: {len(df_mun_cmi)}")
                else:
                    st.write("Sem dados no período")
            
            with col2:
                st.markdown("**CMI-Mil (Factual)**")
                if not df_mun_mil.empty:
                    st.write(f"Período: {df_mun_mil['Ano'].min()} - {df_mun_mil['Ano'].max()}")
                    st.write(f"Média: {df_mun_mil['Valor'].mean():.2f} ‰")
                    st.write(f"Registros: {len(df_mun_mil)}")
                else:
                    st.write("Sem dados no período")

# Rodapé
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888; padding: 20px;'>
    <p>APP3 - Dashboard de Análise de CMI & CMI-Mil</p>
    <p>Dados extraídos de CMI.ods e CMI-Mil.ods</p>
</div>
""", unsafe_allow_html=True)
