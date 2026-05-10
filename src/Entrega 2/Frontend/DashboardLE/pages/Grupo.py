import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from streamlit_cookies_manager import EncryptedCookieManager

from Variaveis.Variaveis import buscarURL, buscarChave

# 1. Configuração da página (deve ser a primeira instrução Streamlit)
st.set_page_config(page_title="Dashboard de Arrecadação", page_icon="📊", layout="wide")

cookies = EncryptedCookieManager(password=buscarChave())
apiURL = buscarURL()

if not cookies.ready():
    st.stop()

# ------------------ HEADER ------------------
col1, col2 = st.columns([1, 4])

with col1:
    st.image("./assets/liderancas_logo.avif", width=120)

with col2:
    st.title("Lideranças Empáticas")
    st.caption("Gestão de grupos e arrecadações")

st.divider()

if not cookies.get("nome"):
    st.error("🔒 Área exclusiva para usuários logados.")
    st.stop()

def get_available_options(nomes, selecionados):
    return ["Selecionar..."] + [n for n in nomes if n not in selecionados]

# 2. Card
def card(title, text):
    st.markdown(f"""
    <div style="
        padding: 20px;
        border-radius: 12px;
        border: 1px solid rgba(128, 128, 128, 0.2);
        background-color: rgba(128, 128, 128, 0.05);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
    ">
        <h4 style="margin-top: 0; color: #1f77b4; font-family: sans-serif;">{title}</h4>
        <div style="font-size: 15px; line-height: 1.6; color: inherit;">{text}</div>
    </div>
    """, unsafe_allow_html=True)


def round_image(url, size=120):
    st.markdown(f"""
    <img src="{url}" 
         style="
             width:{size}px;
             height:{size}px;
             border-radius:50%;
             object-fit:cover;
             box-shadow: 0 4px 8px rgba(0,0,0,0.1);
         ">
    """, unsafe_allow_html=True)


nome = cookies['nome']
email = cookies['email']
grupo = cookies['grupo']

if grupo == "Nenhum":
    # 3. Formulário de criação de grupo alinhado e moderno
    st.title("✨ Crie o seu grupo")
    st.info("💡 Somente um membro deve criar o grupo. Adicione sua equipe abaixo.")

    resposta = requests.get(apiURL + "/buscaralunos")
    alunos = resposta.json()
    nomes = [aluno["nome"] for aluno in alunos]

    with st.container():
        nomeGrupo = st.text_input("Nome do Grupo", placeholder="Ex: Os Arrecadadores", value="")

        # Usando colunas para organizar os inputs
        # Usando colunas para organizar os inputs
        col1, col2 = st.columns(2)
        with col1:
            mentor = st.selectbox("Mentor", ["Selecionar...", "João", "Maria", "Jêsus"])
            integ1 = st.selectbox("Integrante 1 (Você)", [nome])

            # Filtra o próprio usuário logado das opções
            opcoes_2 = get_available_options(nomes, [nome])
            integ2 = st.selectbox("Integrante 2", opcoes_2)

        with col2:
            # Adiciona o integ2 à lista de bloqueados (se ele tiver selecionado alguém)
            selecionados_2 = [nome]
            if integ2 != "Selecionar...":
                selecionados_2.append(integ2)

            opcoes_3 = get_available_options(nomes, selecionados_2)
            integ3 = st.selectbox("Integrante 3", opcoes_3)

            # Adiciona o integ3 à lista de bloqueados (se ele tiver selecionado alguém)
            selecionados_3 = selecionados_2.copy()
            if integ3 != "Selecionar...":
                selecionados_3.append(integ3)

            opcoes_4 = get_available_options(nomes, selecionados_3)
            integ4 = st.selectbox("Integrante 4", opcoes_4)

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("🚀 Criar Grupo", use_container_width=True, type="primary"):
            if integ1 is not "Selecionar..." and integ2 is not "Selecionar..." and integ3 is not "Selecionar..." and integ4 is not "Selecionar..." and mentor is not "Selecionar..." and nomeGrupo is not "":
                dados = {
                    "nomegrupo": nomeGrupo,
                    "mentor": mentor,
                    "integrante1": integ1,
                    "integrante2": integ2,
                    "integrante3": integ3,
                    "integrante4": integ4
                }
                respostaGrupo = requests.post(apiURL + "/criargrupo", data=dados)
                if respostaGrupo.status_code == 200:
                    st.success("Grupo criado com sucesso!")
                    cookies["grupo"] = nomeGrupo
                    st.rerun()
                else:
                    st.error("Erro ao criar o grupo")
                    st.error(respostaGrupo.text)
            else:
                st.warning("Você deve preencher todos os campos!")
else:
    data = {"email": email}
    resposta = requests.post(apiURL + "/buscargrupo", data=data)
    respostaGrupo = resposta.json()
    cookies["grupo"] = str(respostaGrupo["idgrupo"])
    dataAlimentos = {"idgrupo": respostaGrupo["idgrupo"]}
    alimentosResposta = requests.post(apiURL + "/buscarAlimentosGrupo", data=dataAlimentos)
    dadosAlimentos = alimentosResposta.json()

    df = pd.DataFrame(dadosAlimentos)
    if "framecaminho" in df.columns:
        df["framecaminho"] = df["framecaminho"].apply(
            lambda x: f"{apiURL}/uploads/{x}" if pd.notnull(x) and x != "" else None
        )


    if cookies.get("nomegrupo") != respostaGrupo["nomeGrupo"]:
        cookies["nomegrupo"] = respostaGrupo["nomeGrupo"]

    mentor = respostaGrupo["mentor"]
    kgArrecadado = float(respostaGrupo["kgs"])
    integrante2 = respostaGrupo["integrante2"]
    integrante3 = respostaGrupo["integrante3"]
    integrante4 = respostaGrupo["integrante4"]

    # 4. Cabeçalho principal
    st.title(f"🏆 Grupo: {respostaGrupo['nomeGrupo']}")
    st.markdown("---")

    # 5. Métricas em destaque no topo (Substitui o excesso de texto no card)
    m1, m2, m3 = st.columns(3)
    m1.metric("📦 Total Arrecadado", f"{kgArrecadado:.2f} kg")
    m2.metric("🧑‍🏫 Mentor", mentor)
    m3.metric("👥 Equipe", "4 Integrantes")

    # Expandir para ver integrantes, mantendo a tela inicial limpa
    with st.expander("Visualizar integrantes do grupo"):
        st.write(f"- **{nome}** (Você)")
        st.write(f"- {integrante2}")
        st.write(f"- {integrante3}")
        st.write(f"- {integrante4}")

    st.markdown("<br>", unsafe_allow_html=True)

    if "peso" in df.columns:
        df["peso"] = pd.to_numeric(df["peso"], errors="coerce")
        df["dataHora"] = pd.to_datetime(df["dataHora"])
        df = df.sort_values(by="dataHora", ascending=False)

        st.subheader("📊 Análises de Arrecadação")

        # 6. Gráficos lado a lado
        col_grafico1, col_grafico2 = st.columns(2)

        with col_grafico1:
            st.markdown("##### 📈 Evolução das arrecadações")
            df_linha = df.copy()
            df_linha["data"] = df_linha["dataHora"].dt.date
            df_linha = df_linha.groupby("data")["peso"].sum().reset_index()
            df_linha = df_linha.sort_values("data")
            st.line_chart(df_linha.set_index("data"), use_container_width=True)

        with col_grafico2:
            st.markdown("##### 🍩 Distribuição por Alimento")
            df_rosca = df.groupby("nome")["peso"].sum().reset_index()
            fig = px.pie(
                df_rosca,
                names="nome",
                values="peso",
                hole=0.5
            )
            # Ajuste no layout do plotly para ficar mais integrado ao Streamlit
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(margin=dict(t=20, b=20, l=20, r=20), showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        # 7. Tabela Editável (Usando Callbacks) e Filtros
        st.markdown("---")
        st.subheader("📋 Histórico de Arrecadação (Editável)")
        st.caption("Qualquer alteração ou exclusão feita na tabela será salva automaticamente.")
        # Guardamos o DF ordenado base
        df = df.sort_values(by="dataHora", ascending=False).reset_index(drop=True)
        # --- SISTEMA DE FILTRO ---
        col_filtro1, col_filtro2 = st.columns(2)
        with col_filtro1:
            coluna_filtro = st.selectbox(
                "Filtrar por categoria:",
                ["Sem filtro", "nome", "marca", "nomeIntegrante"],
                format_func=lambda x: x.capitalize() if x != "Sem filtro" else x,
                key="filtro_categoria_grupo"
            )
        df_filtrado = df.copy()
        if coluna_filtro != "Sem filtro":
            with col_filtro2:
                # Pega os valores únicos da coluna selecionada
                valores_unicos = df_filtrado[coluna_filtro].dropna().unique().tolist()
                valor_selecionado = st.selectbox(
                    f"Selecione o item:",
                    ["Todos"] + valores_unicos,
                    key="filtro_valor_grupo"
                )
            if valor_selecionado != "Todos":
                df_filtrado = df_filtrado[df_filtrado[coluna_filtro] == valor_selecionado]
        # RESETAMOS O ÍNDICE DO DF FILTRADO PARA NÃO QUEBRAR A EDIÇÃO!
        df_filtrado = df_filtrado.reset_index(drop=True)
        st.session_state["df_atual"] = df_filtrado
        editor_key = "tabela_alimentos"
        # Função de Callback: Roda assim que o usuário clica fora da célula editada ou deleta uma linha
        def processar_tabela():
            mudancas = st.session_state[editor_key]
            houve_alteracao = False
            df_ref = st.session_state["df_atual"]
            # 1. Processar Exclusões
            for idx in mudancas.get("deleted_rows", []):
                id_alimento = df_ref.iloc[idx]["id"]
                requests.post(apiURL + "/excluirAlimento", json={"id": int(id_alimento)})
                houve_alteracao = True
            # 2. Processar Edições
            for idx, modificacoes in mudancas.get("edited_rows", {}).items():
                linha_original = df_ref.iloc[idx]
                dados_update = {
                    "id": int(linha_original["id"]),
                    "nome": modificacoes.get("nome", linha_original["nome"]),
                    "marca": modificacoes.get("marca", linha_original["marca"]),
                    "quantidade": int(modificacoes.get("quantidade", linha_original["quantidade"])),
                    "peso": float(modificacoes.get("peso", linha_original["peso"]))
                }
                requests.post(apiURL + "/editarAlimento", json=dados_update)
                houve_alteracao = True
            if houve_alteracao:
                st.toast("✅ Alterações salvas com sucesso no banco de dados!")
        # O st.data_editor aciona a função 'processar_tabela'
        st.data_editor(
            df_filtrado,  # <-- Passamos o DF Filtrado aqui
            use_container_width=True,
            hide_index=True,
            num_rows="dynamic",
            disabled=["id", "dataHora", "idGrupo", "framecaminho"],
            key=editor_key,
            on_change=processar_tabela,
            column_config={
                "framecaminho": st.column_config.ImageColumn("Imagem")
            }
        )
    else:
        st.warning("O grupo ainda não realizou uma captura!")
