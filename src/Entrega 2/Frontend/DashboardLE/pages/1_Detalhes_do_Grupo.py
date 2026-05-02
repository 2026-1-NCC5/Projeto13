import streamlit as st
import requests
import pandas as pd
import plotly.express as px

from Variaveis.Variaveis import buscarURL

# ------------------ CONFIG ------------------
st.set_page_config(page_title="Detalhes do Grupo", layout="wide")
apiURL = buscarURL()

# ------------------ VALIDAÇÃO DA SESSÃO ------------------
# Verifica se o usuário chegou aqui clicando em um grupo no Dashboard
if "grupo" not in st.session_state or "integrantes" not in st.session_state:
    st.warning("Nenhum grupo selecionado. Por favor, volte ao Dashboard e selecione um grupo.")
    if st.button("Voltar ao Dashboard"):
        st.switch_page("Dashboard.py")
    st.stop()

grupo = st.session_state.grupo
integrantes = st.session_state.integrantes

# ------------------ BOTÃO DE VOLTAR ------------------
if st.button("← Voltar ao Dashboard"):
    st.switch_page("Dashboard.py")

# ------------------ HEADER DO GRUPO ------------------
st.title(f"📊 Equipe: {grupo['nomeGrupo']}")
st.markdown(f"**Mentor:** {grupo['mentor']} | **Total Arrecadado Oficial:** {grupo['kgArrecadados']} kg")

with st.expander("Ver Integrantes da Equipe"):
    for integrante in integrantes:
        st.markdown(f"- 👤 {integrante['nome']}")

st.divider()


# ------------------ BUSCA DE DADOS (HISTÓRICO) ------------------
@st.cache_data(ttl=60)  # Cache de 1 minuto para não sobrecarregar o banco
def buscar_historico_alimentos(id_grupo):
    try:
        # Pelo seu server.js, a rota espera req.body.idgrupo
        response = requests.post(f"{apiURL}/buscarAlimentosGrupo", json={"idgrupo": id_grupo})
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Erro ao buscar histórico de alimentos: {e}")
        return []


dados_alimentos = buscar_historico_alimentos(grupo['id'])

# ------------------ RENDERIZAÇÃO DOS INSIGHTS E GRÁFICOS ------------------
if not dados_alimentos:
    st.info("Este grupo ainda não possui registros de arrecadação de alimentos no histórico.")
else:
    # Converte JSON para Pandas DataFrame para facilitar a análise
    df = pd.DataFrame(dados_alimentos)

    # Tratamento de datas
    df['dataHora'] = pd.to_datetime(df['dataHora'])
    df['Data'] = df['dataHora'].dt.strftime('%d/%m/%Y')

    # 1. KPIs / INSIGHTS RÁPIDOS
    st.subheader("💡 Insights da Arrecadação")
    col1, col2, col3, col4 = st.columns(4)

    total_itens_diferentes = df['nome'].nunique()
    total_doacoes = len(df)
    item_mais_doado = df.groupby('nome')['quantidade'].sum().idxmax()
    maior_doacao_peso = df['peso'].max()

    col1.metric("Doações Registradas", total_doacoes)
    col2.metric("Itens Diferentes", total_itens_diferentes)
    col3.metric("Item Mais Frequente", item_mais_doado.title())
    col4.metric("Maior Doação Única", f"{maior_doacao_peso:.2f} kg")

    st.markdown("##")

    # 2. GRÁFICOS
    col_grafico1, col_grafico2 = st.columns(2)

    with col_grafico1:
        # Gráfico de Linha: Evolução das arrecadações ao longo do tempo
        st.markdown("#### Evolução de Arrecadação (kg)")
        df_timeline = df.groupby('Data')['peso'].sum().reset_index()
        fig_linha = px.line(df_timeline, x='Data', y='peso', markers=True,
                            labels={'peso': 'Quilos (kg)', 'Data': 'Data da Doação'},
                            color_discrete_sequence=['#1f77b4'])
        st.plotly_chart(fig_linha, use_container_width=True)

    with col_grafico2:
        # Gráfico de Barras: Top Alimentos Arrecadados por Peso
        st.markdown("#### Top Alimentos por Peso (kg)")
        df_top_alimentos = df.groupby('nome')['peso'].sum().reset_index().sort_values('peso', ascending=False).head(5)
        fig_barras = px.bar(df_top_alimentos, x='peso', y='nome', orientation='h',
                            labels={'peso': 'Quilos (kg)', 'nome': 'Alimento'},
                            color='peso', color_continuous_scale='Blues')
        fig_barras.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_barras, use_container_width=True)

    st.divider()

    # 3. TABELA DE HISTÓRICO COMPLETO
    st.subheader("📋 Histórico Completo de Entradas")

    # Organizando as colunas para exibição
    df_exibicao = df[['id', 'nome', 'marca', 'quantidade', 'peso', 'dataHora']].copy()
    df_exibicao.rename(columns={
        'id': 'ID',
        'nome': 'Alimento',
        'marca': 'Marca',
        'quantidade': 'Qtd',
        'peso': 'Peso (kg)',
        'dataHora': 'Data e Hora'
    }, inplace=True)

    df_exibicao['Data e Hora'] = df_exibicao['Data e Hora'].dt.strftime('%d/%m/%Y %H:%M:%S')
    df_exibicao.sort_values('ID', ascending=False, inplace=True)

    st.dataframe(
        df_exibicao,
        use_container_width=True,
        hide_index=True
    )