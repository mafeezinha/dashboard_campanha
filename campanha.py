import streamlit as st
import pandas as pd
import plotly.express as px
import os

# CONFIGURAÇÃO DA PÁGINA 
st.set_page_config(
    page_title="Dashboard - Campanha do Agasalho",
    page_icon="🧥",
    layout="wide"
)

st.title("🧥 Dashboard Interativo: Campanha do Agasalho")
st.markdown("Comparativo do volume de peças arrecadadas entre **2024 e 2025** e variação por grupo de vestuário.")

# CARREGAMENTO DOS DADOS 
if os.path.exists('campanha_do_agasalho.xlsx'):
    excel_path = 'campanha_do_agasalho.xlsx'
elif os.path.exists('Dados/campanha_do_agasalho.xlsx'):
    excel_path = 'Dados/campanha_do_agasalho.xlsx'
else:
    excel_path = 'campanha_do_agasalho.xlsx'

@st.cache_data
def load_data(path):
    df = pd.read_excel(path, sheet_name='Campanha do Agasalho')
    return df

try:
    df_campanha = load_data(excel_path)
except Exception as e:
    st.error(f"Erro ao carregar a planilha '{excel_path}': {e}")
    st.stop()

# Separar os dados individuais do Total Geral
df_itens = df_campanha[df_campanha['Grupo de Vestuário'] != 'TOTAL GERAL DE ROUPAS'].copy()
df_total = df_campanha[df_campanha['Grupo de Vestuário'] == 'TOTAL GERAL DE ROUPAS'].iloc[0]

# METRICAS DE RESUMO (KPIs) 
col1, col2, col3 = st.columns(3)
col1.metric(
    label="📦 Volume 2024 (Peças)", 
    value=f"{df_total['Volume 2024 (Peças)']:,.0f}".replace(",", ".")
)
col2.metric(
    label="🚀 Volume 2025 (Peças)", 
    value=f"{df_total['Volume 2025 (Peças)']:,.0f}".replace(",", "."),
    delta=f"+{df_total['Variação Absoluta']:,.0f}".replace(",", ".")
)
col3.metric(
    label="📈 Crescimento Total", 
    value=f"{((df_total['Volume 2025 (Peças)'] / df_total['Volume 2024 (Peças)']) - 1) * 100:.1f}%"
)

st.markdown("---")

# NAVEGAÇÃO E FILTROS NA BARRA LATERAL
st.sidebar.header("🔍 Opções de Visualização")
categoria_selecionada = st.sidebar.multiselect(
    "Filtrar Grupos de Vestuário:",
    options=df_itens['Grupo de Vestuário'].tolist(),
    default=df_itens['Grupo de Vestuário'].tolist()
)

df_filtrado = df_itens[df_itens['Grupo de Vestuário'].isin(categoria_selecionada)]

# --- VISUALIZAÇÕES E GRÁFICOS ---
col_g1, col_g2 = st.columns(2)

with col_g1:
    st.subheader("Comparativo de Arrecadação (2024 vs 2025)")
    
    # Transformar dados para formato longo (necessário para gráfico comparativo lado a lado)
    df_melted = df_filtrado.melt(
        id_vars=['Grupo de Vestuário'], 
        value_vars=['Volume 2024 (Peças)', 'Volume 2025 (Peças)'],
        var_name='Ano', 
        value_name='Volume'
    )
    df_melted['Ano'] = df_melted['Ano'].str.extract(r'(\d{4})')
    
    fig_comp = px.bar(
        df_melted,
        x='Grupo de Vestuário',
        y='Volume',
        color='Ano',
        barmode='group',
        text_auto=',.0f',
        title="Volume por Ano e Categoria"
    )
    st.plotly_chart(fig_comp, use_container_width=True)

with col_g2:
    st.subheader("Crescimento Absoluto por Categoria")
    fig_var = px.bar(
        df_filtrado,
        x='Variação Absoluta',
        y='Grupo de Vestuário',
        orientation='h',
        color='Variação Absoluta',
        text_auto=',.0f',
        title="Aumento do Volume de Peças (2024 a 2025)"
    )
    st.plotly_chart(fig_var, use_container_width=True)

# --- TABELA DE DADOS DETALHADA ---
st.markdown("---")
st.subheader("📋 Tabela Detalhada dos Dados")
st.dataframe(df_campanha, use_container_width=True)