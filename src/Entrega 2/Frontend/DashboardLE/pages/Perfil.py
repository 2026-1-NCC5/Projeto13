import requests
import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager

from Variaveis.Variaveis import buscarURL, buscarChave

# 1. Configuração da página (centralizada para ficar com cara de perfil)
st.set_page_config(page_title="Meu Perfil", page_icon="👤", layout="centered")

apiURL = buscarURL()
cookies = EncryptedCookieManager(password=buscarChave())

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

nome = cookies['nome']
email = cookies['email']
grupo = cookies['grupo']
fotoPerfil = None

# 2. Cabeçalho
st.title("👤 Meu Perfil")
st.markdown("---")

# 3. Colunas com proporção 1:2 (A foto ocupa menos espaço, os dados ocupam mais)
col_foto, col_info = st.columns([1, 2], gap="large")

with col_foto:
    if not cookies.get('foto'):
        # Placeholder visual se o usuário não tiver foto
        st.markdown("""
        <div style="display: flex; justify-content: center; margin-bottom: 20px;">
            <div style="width: 180px; height: 180px; border-radius: 50%; background-color: rgba(128,128,128,0.1); display: flex; align-items: center; justify-content: center; border: 2px dashed #ccc;">
                <span style="font-size: 50px; color: #aaa;">📷</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        fotoPerfil = st.file_uploader("Adicionar foto", type=["png", "jpg", "jpeg"])
    else:
        caminhoImagem = apiURL + "/uploads/" + cookies['foto']
        # HTML/CSS para forçar a imagem a ficar redonda, com borda e sombra
        st.markdown(f"""
        <div style="display: flex; justify-content: center; margin-bottom: 20px;">
            <img src="{caminhoImagem}" 
                 style="
                     width: 180px; 
                     height: 180px; 
                     border-radius: 50%; 
                     object-fit: cover; 
                     border: 3px solid #1f77b4; 
                     box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                 ">
        </div>
        """, unsafe_allow_html=True)
        # Continua permitindo que o usuário troque a foto
        fotoPerfil = st.file_uploader("Trocar foto", type=["png", "jpg", "jpeg"])

with col_info:
    st.subheader("Meus Dados")
    if cookies.get('nomegrupo'):
        nomeGrupo = cookies['nomeGrupo']
    else:
        nomeGrupo = "Nenhum"
    # 4. Uso de st.text_input desabilitado cria um visual de "card de dados" muito mais profissional que st.text
    st.text_input("Nome Completo", value=nome, disabled=True)
    st.text_input("Endereço de Email", value=email, disabled=True)
    st.text_input("Grupo Atual", value=nomeGrupo, disabled=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 5. Botão de saída estilizado
    sairbtn = st.button("🚪 Sair da Conta", type="primary", use_container_width=True)

# Lógica de Logout (Adicionado cookies.save() por segurança)
if sairbtn:
    del cookies["nome"]
    del cookies['email']
    del cookies['grupo']
    if cookies.get('nomegrupo'):
        del cookies['nomegrupo']
    if cookies.get('foto'):
        del cookies['foto']
    cookies.save()  # Salva as exclusões antes de redirecionar
    st.switch_page("./pages/Entrar.py")

# Lógica de Upload de Foto
if fotoPerfil is not None:
    # Adicionado um spinner para feedback visual de carregamento
    with st.spinner("Salvando foto de perfil..."):
        arquivo = {
            "foto": (fotoPerfil.name, fotoPerfil, fotoPerfil.type)
        }
        dados = {
            "email": email
        }
        resposta = requests.post(apiURL + "/fotoperfil", files=arquivo, data=dados)

        if resposta.status_code == 200:
            st.success("✅ Foto enviada com sucesso!")
            cookies["foto"] = fotoPerfil.name
            cookies.save()
            st.rerun()
        else:
            st.error(f"❌ Erro ao enviar a foto. {resposta.text}")