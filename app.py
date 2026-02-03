import streamlit as st
import pandas as pd
import plotly.express as px
import pycountry

# ativar venv por .venv\Scripts\activate
# python recomendado 3.12
# pip install -r requirements.txt
# rodar com streamlit run app.py

def iso2_to_iso3(code):
    try:
        return pycountry.countries.get(alpha_2=code).alpha_3
    except:
        return None

# layout, ícone, título
st.set_page_config(
    page_title="Dashboard de Salários em Dados", 
    page_icon="📊", 
    layout="wide")

# carregando os dados
df = pd.read_csv("https://raw.githubusercontent.com/vqrca/dashboard_salarios_dados/refs/heads/main/dados-imersao-final.csv")
st.sidebar.header("Filtros 🔍")

#filtros de ano, senioridade, tipo de contrato, tamanho da empresa
anos_disponiveis = df["ano"].unique().tolist()
anos_selecionados = st.sidebar.multiselect("Ano", anos_disponiveis, anos_disponiveis)

senioridades_disponiveis = df["senioridade"].unique().tolist()
senioridades_selecionadas = st.sidebar.multiselect("Senioridade", senioridades_disponiveis, senioridades_disponiveis)

tipos_de_contratos_disponiveis = df["contrato"].unique().tolist()
contratos_selecionados = st.sidebar.multiselect("Tipo de Contrato", tipos_de_contratos_disponiveis, tipos_de_contratos_disponiveis)


tamanhos_de_empresas_disponiveis = df["tamanho_empresa"].unique().tolist()
st.sidebar.multiselect("Tamanho da Empresa", tamanhos_de_empresas_disponiveis, tamanhos_de_empresas_disponiveis)

#filtrando os dados
df_filtrado = df[
                 (df["ano"].isin(anos_selecionados)) &
                 (df["senioridade"].isin(senioridades_selecionadas)) &
                 (df["contrato"].isin(contratos_selecionados)) &
                 (df["tamanho_empresa"].isin(tamanhos_de_empresas_disponiveis))
]

st.title("Dashboard de Salários em Dados")
st.markdown("Explore os salários da área de dados")

# métricas principais KPIs

st.subheader("KPIs Principais")

if not df_filtrado.empty:
    salario_medio = df_filtrado["usd"].mean()
    salario_maximo = df_filtrado["usd"].max()
    total_registros = df_filtrado["cargo"].shape[0]
    cargo_mais_frequente = df_filtrado["cargo"].mode()[0]
else:
    salario_medio, salario_maximo, total_registros, cargo_mais_frequente = 0, 0, 0, ""

col1, col2, col3, col4 = st.columns(4)
col1.metric("Salário Médio", f"${salario_medio:,.0f}")
col2.metric("Salário Máximo", f"${salario_maximo:,.0f}")
col3.metric("Total de Registros", f"${total_registros:,}")
col4.metric("Cargo Mais Frequente", cargo_mais_frequente)

st.markdown("---")

st.subheader("Gráficos")

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    if not df_filtrado.empty:
        top_cargos = df_filtrado.groupby("cargo")["usd"].mean().nlargest(10).sort_values(ascending=True).reset_index()
        grafico_cargos = px.bar(
            top_cargos,
            x='usd',
            y='cargo',
            orientation='h',
            title='Top 10 cargos por salário médio',
            labels={'usd': 'Média Salarial anual (USD)', 'cargo': ''}
        )
        grafico_cargos.update_layout(title_x=0.1, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(grafico_cargos, use_container_width=True)
    else:
        st.warning('Nenhum dado para exibir no gráfico')
    
with col_graf2:
    if not df_filtrado.empty:
        grafico_hist = px.histogram(
            df_filtrado,
            x='usd',
            nbins=30,
            title='Distribuição de salários anuais',
            labels={'usd': 'Salário anual (USD)'}
        )
        grafico_hist.update_layout(title_x=0.1)
        st.plotly_chart(grafico_hist, use_container_width=True)
    else:
        st.warning('Nenhum dado para exibir no gráfico de distribuição')
    
col_graf3, col_graf4 = st.columns(2)

with col_graf3:
    if not df_filtrado.empty:
        contagem_remoto = df_filtrado['remoto'].value_counts().reset_index()
        contagem_remoto.columns = ['tipo_trabalho', 'qtde']

        graf_remoto = px.pie(contagem_remoto,
                    names='tipo_trabalho',
                    values='qtde', # Corrigido de 'quantidade' para 'qtde'
                    title='proporção dos tipos de trabalho',
                    hole=0.5)
        graf_remoto.update_traces(textinfo='percent+label')
        graf_remoto.update_layout(title_x=0.1)
        st.plotly_chart(graf_remoto, use_container_with_width=True)
    else:
        st.warning('Nenhum dado para exibir no gráfico de tipos de trabalho')
        
df_filtrado['residencia_iso3'] = df_filtrado['residencia'].apply(iso2_to_iso3)
with col_graf4:
    if not df_filtrado.empty:
        df_ds = df_filtrado[df_filtrado['cargo'] == 'Data Scientist']
        media_ds_pais = df_ds.groupby('residencia_iso3')['usd'].mean().reset_index()
        fig4 = px.choropleth(media_ds_pais,
                            locations='residencia_iso3',
                            color='usd',
                            color_continuous_scale='rdylgn',
                            title='Salário médio de cientista de dados por país',
                            labels={'usd': 'Salário médio (USD)', 'residencia_iso3': 'País'})
        fig4.update_layout(title_x=0.1)
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.warning('Nenhum dado para exibir no gráfico de salários por país')

st.subheader('Dados detalhados:')
st.dataframe(df_filtrado)
