import pandas as pd
import requests
import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager

from Variaveis.Variaveis import buscarURL, buscarChave

# ------------------ CONFIG ------------------
st.set_page_config(page_title="Lideranças Empáticas", layout="wide")

cookies = EncryptedCookieManager(password=buscarChave())
apiURL = buscarURL()

if not cookies.ready():
    st.stop()

# ------------------ STYLE ------------------
st.markdown("""
<style>
[data-testid="stContainer"] {
    border-radius: 12px;
    padding: 16px;
    background-color: #fafafa;
    box-shadow: 0 2px 6px rgba(0,0,0,0.05);
}
</style>
""", unsafe_allow_html=True)

# ------------------ HEADER ------------------
col1, col2 = st.columns([1, 4])

with col1:
    st.image("./assets/liderancas_logo.avif", width=120)

with col2:
    st.title("Lideranças Empáticas")
    st.caption("Gestão de grupos e arrecadações")

st.divider()

def buscar_grupos():
    response = requests.get(apiURL + "/grupos")
    response.raise_for_status()
    return response.json()

def buscar_integrantes(id_grupo):
    response = requests.post(apiURL + "/buscarIntegrantes", data={"idGrupo": id_grupo})
    response.raise_for_status()
    return response.json()

# ------------------ CARD ------------------
def GrupoCard(grupo, integrantes):
    with st.container(border=True):
        st.markdown(f"### {grupo['nomeGrupo']}")

        col1, col2, col3 = st.columns([2, 2, 1])

        # LEFT: Mentor + integrantes
        with col1:
            st.markdown(f"👤 **Mentor:** {grupo['mentor']}")

        # MIDDLE: Metric
        with col2:
            st.metric(
                label="Total arrecadado",
                value=f"{grupo['kgArrecadados']:.2f} kg"
            )

            if grupo["kgArrecadados"] > 100:
                st.success("🔥 Grupo destaque!")

        # RIGHT: Button
        with col3:
            if st.button("Ver", key=f"btn_{grupo['id']}", width=200):
                st.session_state.grupo = grupo
                st.session_state.integrantes = integrantes
                # Adicione esta linha para navegar para a nova página
                st.switch_page("./pages/1_Detalhes_do_Grupo.py")
        with st.expander("Visualizar integrantes do grupo"):
            for integrante in integrantes:
                st.markdown(f"- {integrante['nome']}")
        st.divider()

# ------------------ MAIN ------------------
try:
    grupos = buscar_grupos()

    # Ordenar os grupos por kg arrecadados (do maior para o menor)
    grupos_ordenados = sorted(grupos, key=lambda x: float(x.get("kgArrecadados", 0)), reverse=True)

    # --- SISTEMA DE RANKING ---
    st.subheader("🏆 Ranking Geral de Arrecadações")
    if grupos_ordenados:
        # Cria um DataFrame limpo apenas para o ranking
        df_ranking = pd.DataFrame(grupos_ordenados)
        df_ranking = df_ranking[['nomeGrupo', 'mentor', 'kgArrecadados']]
        df_ranking.index = df_ranking.index + 1  # Para a posição começar do 1º
        df_ranking.columns = ['Nome do Grupo', 'Mentor', 'Total Arrecadado (Kg)']

        # Exibe a tabela de ranking
        st.dataframe(df_ranking, use_container_width=True)
    else:
        st.info("Nenhum grupo com arrecadação registrada ainda.")

    st.divider()

    colt1, colt2 = st.columns(2)
    with colt1:
        st.subheader("Detalhes dos Grupos")
    with colt2:
        filtro = st.selectbox(
            "Filtro",
            ["Maior arrecadação", "Menor arrecadação", "Mais recente", "Mais antigo"]
        )

    # Aplicar ordenação baseada no filtro
    if filtro == "Maior arrecadação":
        grupos_ordenados = sorted(
            grupos,
            key=lambda x: float(x.get("kgArrecadados", 0)),
            reverse=True
        )

    elif filtro == "Menor arrecadação":
        grupos_ordenados = sorted(
            grupos,
            key=lambda x: float(x.get("kgArrecadados", 0))
        )

    elif filtro == "Mais recente":
        grupos_ordenados = sorted(
            grupos,
            key=lambda x: int(x.get("id", 0)),
            reverse=True
        )

    elif filtro == "Mais antigo":
        grupos_ordenados = sorted(
            grupos,
            key=lambda x: int(x.get("id", 0))
        )

    else:
        grupos_ordenados = grupos
    for i, grupo in enumerate(grupos_ordenados):
        try:
            integrantes = buscar_integrantes(grupo["id"])
            GrupoCard(grupo, integrantes)
            st.markdown("##")  # spacing
        except requests.RequestException as e:
            st.error(f"Erro ao buscar integrantes: {e}")

except requests.RequestException as e:
    st.error(f"Erro ao buscar grupos: {e}")