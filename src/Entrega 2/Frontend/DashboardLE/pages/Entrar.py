import streamlit as st
import requests
from streamlit_cookies_manager import EncryptedCookieManager

from Variaveis.Variaveis import buscarURL, buscarChave

cookies = EncryptedCookieManager(password=buscarChave())

if not cookies.ready():
    st.stop()

if cookies.get("nome"):
    st.success("Usuário já logado!")
    st.stop()

apiURL = buscarURL()

st.title("Login")
opcao = st.radio("Selecione uma opção", ["Login", "Cadastro"])

if opcao == "Login":
    emailLogin = st.text_input("Email")
    senhaLogin = st.text_input("Senha", type="password")
    if st.button("Entrar") and opcao == "Login":
        if not emailLogin and not senhaLogin:
            st.error("Preencha todos os campos!", )
        else:
            dados = {
                "email": emailLogin,
                "senha": senhaLogin
            }
            loginURL = apiURL + "/login"
            try:
                resposta = requests.post(loginURL, json=dados)
                if resposta.status_code == 200:
                    resultado = resposta.json()
                    cookies["email"] = emailLogin
                    cookies["nome"] = resultado["nome"]
                    idgrupo = resultado["idgrupo"]
                    if idgrupo is not None:
                        cookies["grupo"] = str(idgrupo)
                        nomeGrupo = resultado["nomeGrupo"]
                        cookies['nomegrupo'] = nomeGrupo
                    else:
                        cookies["grupo"] = "Nenhum"
                    dados = {
                        "email": emailLogin
                    }
                    respostaFoto = requests.post(apiURL + "/buscarfoto", data=dados)
                    if respostaFoto.status_code == 200:
                        respostaJson = respostaFoto.json()
                        if respostaJson and "foto" in respostaJson[0]:
                            fotoNome = respostaJson[0]["foto"]
                            if fotoNome:
                                cookies["foto"] = str(fotoNome)
                    cookies.save()
                    st.switch_page("./pages/Perfil.py")
                else:
                    st.error(f"Erro: {resposta.status_code}")
                    st.text(resposta.text)
            except requests.exceptions.RequestException as e:
                st.error(f"Erro de conexão: {e}")
else:
    nomeCadastro = st.text_input("Digite o seu nome:")
    emailCadastro = st.text_input("Digite o seu email:")
    senhaCadastro = st.text_input("Digite a sua senha:", type="password")
    confSenhaCadastro = st.text_input("Confirme a sua senha:", type="password")
    col1, col2 = st.columns(2)
    if st.button("Cadastrar") and opcao == "Cadastro":
        if not nomeCadastro and not emailCadastro and not senhaCadastro and not confSenhaCadastro:
            st.error("Preencha todos os campos!", )
        else:
            if senhaCadastro == confSenhaCadastro:
                dados = {
                    "nome": nomeCadastro,
                    "email": emailCadastro,
                    "senha": senhaCadastro,
                }
                cadastroURL = apiURL + "/cadastro"
                try:
                    resposta = requests.post(cadastroURL, json=dados)
                    if resposta.status_code == 200:
                        cookies["nome"] = nomeCadastro
                        cookies["email"] = emailCadastro
                        cookies["grupo"] = "Nenhum"
                        cookies.save()
                        st.success("Usuário Criado!")
                        st.switch_page("./pages/Perfil.py")
                    else:
                        st.error(f"Erro: {resposta.status_code}")
                        st.text(resposta.text)
                except requests.exceptions.RequestException as e:
                    st.error(f"Erro de conexão: {e}")
            else:
                st.error("As senhas não coincidem!")