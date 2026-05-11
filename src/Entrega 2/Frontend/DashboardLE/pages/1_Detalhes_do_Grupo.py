import streamlit as st
import requests
import pandas as pd
import plotly.express as px

from Variaveis.GerarPDF import gerar_pdf_relatorio_estilizado
from Variaveis.Variaveis import buscarURL

# ------------------ CONFIG ------------------
st.set_page_config(page_title="Detalhes do Grupo", layout="wide")
apiURL = buscarURL()

# ------------------ VALIDAÇÃO DA SESSÃO ------------------
# Verifica se o usuário chegou aqui clicando em um grupo no Dashboard
if "grupo" not in st.session_state or "integrantes" not in st.session_state:
    st.warning("Nenhum grupo selecionado. Por favor, volte ao Dashboard e selecione um grupo.")
    if st.button("Voltar ao Dashboard"):
        st.switch_page("./pages/Dashboard.py")
    st.stop()

grupo = st.session_state.grupo
integrantes = st.session_state.integrantes

# ------------------ HEADER ------------------
col1, col2 = st.columns([1, 4])

with col1:
    st.image("./assets/liderancas_logo.avif", width=120)

with col2:
    st.title("Lideranças Empáticas")
    st.caption("Gestão de grupos e arrecadações")

st.divider()

# ------------------ BOTÃO DE VOLTAR ------------------
if st.button("← Voltar ao Dashboard"):
    st.switch_page("./pages/Dashboard.py")

# ------------------ HEADER DO GRUPO ------------------
st.title(f"📊 Equipe: {grupo['nomeGrupo']}")
st.markdown(f"**Mentor:** {grupo['mentor']} | **Total Arrecadado Oficial:** {grupo['kgArrecadados']:.2f} kg")

with st.expander("Ver Integrantes da Equipe"):
    for integrante in integrantes:
        st.markdown(f"- 👤 {integrante['nome']}")

st.divider()


# ------------------ BUSCA DE DADOS (HISTÓRICO) ------------------
@st.cache_data(ttl=60)  # Cache de 1 minuto para não sobrecarregar o banco
def buscar_historico_alimentos(id_grupo):
    try:
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
        st.plotly_chart(fig_linha, width='stretch')

    with col_grafico2:
        # Gráfico de Barras: Top Alimentos Arrecadados por Peso
        st.markdown("#### Top Alimentos por Peso (kg)")
        df_top_alimentos = df.groupby('nome')['peso'].sum().reset_index().sort_values('peso', ascending=False).head(5)
        fig_barras = px.bar(df_top_alimentos, x='peso', y='nome', orientation='h',
                            labels={'peso': 'Quilos (kg)', 'nome': 'Alimento'},
                            color='peso', color_continuous_scale='Blues')
        fig_barras.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_barras, width='stretch')

    st.divider()

    # 3. TABELA DE HISTÓRICO COMPLETO COM FILTROS
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

    col_tit2, col_btn2 = st.columns([3, 1])
    with col_tit2:
        st.subheader("📋 Histórico Completo de Entradas")

    with col_btn2:
        lista_integrantes_det = [i['nome'] for i in integrantes]
        # Gera o PDF já passando o df_exibicao (que tem os nomes de coluna adaptados)
        # Dentro do with col_btn2:
        pdf_bytes_det = gerar_pdf_relatorio_estilizado(
            grupo['nomeGrupo'],
            grupo['mentor'],
            lista_integrantes_det,
            grupo['kgArrecadados'],
            df_exibicao,
            figs=[fig_linha, fig_barras]  # Passando os dois gráficos da tela
        )
        st.download_button(
            label="📄 Exportar Relatório PDF",
            data=pdf_bytes_det,
            file_name=f"Detalhes_Arrecadacao_{grupo['nomeGrupo']}.pdf",
            mime="application/pdf",
            use_container_width=True,
            type="primary"
        )



    # --- SISTEMA DE FILTRO ---
    col_filtro1, col_filtro2 = st.columns(2)

    with col_filtro1:
        coluna_filtro_det = st.selectbox(
            "Filtrar por categoria:",
            ["Sem filtro", "Alimento", "Marca"],
            key="filtro_categoria_detalhes"
        )

    df_exibicao_filtrado = df_exibicao.copy()

    if coluna_filtro_det != "Sem filtro":
        with col_filtro2:
            valores_unicos_det = df_exibicao_filtrado[coluna_filtro_det].dropna().unique().tolist()
            valor_selecionado_det = st.selectbox(
                f"Selecione o item:",
                ["Todos"] + valores_unicos_det,
                key="filtro_valor_detalhes"
            )

        if valor_selecionado_det != "Todos":
            df_exibicao_filtrado = df_exibicao_filtrado[
                df_exibicao_filtrado[coluna_filtro_det] == valor_selecionado_det]

    # Renderiza a tabela filtrada
    st.dataframe(
        df_exibicao_filtrado,
        width='stretch',
        hide_index=True
    )
