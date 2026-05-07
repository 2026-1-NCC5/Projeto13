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

# 2. Card modernizado (compatível com dark/light mode e com transição suave)
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
        col1, col2 = st.columns(2)
        with col1:
            mentor = st.selectbox("Mentor", ["Selecionar...", "João", "Maria", "Jêsus"])
            integ1 = st.selectbox("Integrante 1 (Você)", [nome])
            integ2 = st.selectbox("Integrante 2", ["Selecionar..."] + nomes)
        with col2:
            integ3 = st.selectbox("Integrante 3", ["Selecionar..."] + nomes)
            integ4 = st.selectbox("Integrante 4", ["Selecionar..."] + nomes)

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
            st.markdown("##### 📈 Evolução Diária")
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
        # 7. Tabela Editável
        st.markdown("---")
        st.subheader("📋 Histórico de Arrecadação (Editável)")
        st.caption(
            "Você pode modificar os valores com um duplo-clique ou excluir uma linha inteira (selecione-a e aperte delete/backspace). Ao finalizar, clique em Salvar.")
        # Resetar o index é fundamental para garantir que as alterações não apontem para a linha errada após ordenar
        df = df.sort_values(by="dataHora", ascending=False).reset_index(drop=True)
        editor_key = "tabela_alimentos"
        # O st.data_editor substitui o st.dataframe
        st.data_editor(
            df,
            use_container_width=True,
            hide_index=True,
            num_rows="dynamic",
            disabled=["id", "dataHora", "idGrupo", "framecaminho"],
            key=editor_key,
            column_config={
                "framecaminho": st.column_config.ImageColumn(
                    "Imagem",
                    help="Imagem capturada no momento da detecção"
                )
            }
        )
        # Botão para processar as modificações
        if st.button("💾 Salvar Alterações da Tabela", type="primary"):
            mudancas = st.session_state[editor_key]
            houve_alteracao = False
            # 1. Processar linhas excluídas
            for idx in mudancas.get("deleted_rows", []):
                id_alimento = df.iloc[idx]["id"]
                resposta = requests.post(apiURL + "/excluirAlimento", json={"id": int(id_alimento)})
                houve_alteracao = True
            # 2. Processar linhas editadas
            for idx, modificacoes_coluna in mudancas.get("edited_rows", {}).items():
                linha_original = df.iloc[idx]
                id_alimento = linha_original["id"]
                # Recupera o valor modificado ou mantém o original se não foi alterado
                novo_nome = modificacoes_coluna.get("nome", linha_original["nome"])
                nova_marca = modificacoes_coluna.get("marca", linha_original["marca"])
                nova_qtd = modificacoes_coluna.get("quantidade", linha_original["quantidade"])
                novo_peso = modificacoes_coluna.get("peso", linha_original["peso"])
                dados_update = {
                    "id": int(id_alimento),
                    "nome": novo_nome,
                    "marca": nova_marca,
                    "quantidade": int(nova_qtd),
                    "peso": float(novo_peso)
                }
                resposta = requests.post(apiURL + "/editarAlimento", json=dados_update)
                houve_alteracao = True
            if houve_alteracao:
                st.success("Tabela e totais do grupo atualizados com sucesso!")
                st.rerun()  # Atualiza a página para refletir os novos dados nos gráficos e métricas
            else:
                st.warning("Nenhuma alteração foi detectada para salvar.")
    else:
        st.warning("O grupo ainda não realizou uma captura!")
