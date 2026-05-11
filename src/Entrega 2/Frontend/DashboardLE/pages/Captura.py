import datetime
import base64
from io import BytesIO
from PIL import Image
import numpy as np
import math

import streamlit as st
import cv2
import requests
from ultralytics import YOLO
from collections import Counter
from streamlit_cookies_manager import EncryptedCookieManager
from streamlit_shortcuts import shortcut_button

from Variaveis.Variaveis import buscarURL, buscarChave, buscarVideoURL

apiURL = buscarURL()

# ==============================================================================
# CALIBRAÇÃO PARA MEDIÇÃO DE TAMANHO/PESO
# ==============================================================================

# Pontos obtidos do calibrador
pontos_imagem_pixel = np.array(
    [[47, 31], [555, 32], [558, 443], [60, 432]],
    dtype="float32"
)

# Medidas reais da superfície em cm
pontos_real_cm = np.array([
    [0, 0],
    [50, 0],
    [50, 50],
    [0, 50]
], dtype="float32")

# Matriz de conversão pixel -> cm
matriz_medidas, _ = cv2.findHomography(
    pontos_imagem_pixel,
    pontos_real_cm
)

cookies = EncryptedCookieManager(password=buscarChave())

if not cookies.ready():
    st.stop()

if not cookies.get("nome"):
    st.error("Área exclusiva para usuários logados.")
    st.stop()
if not cookies.get("nomegrupo"):
    st.error("Área exclusiva para usuários com grupo.")
    st.stop()

grupo = cookies['grupo']

# ------------------ HEADER ------------------
col1, col2 = st.columns([1, 4])

with col1:
    st.image("./assets/liderancas_logo.avif", width=120)

with col2:
    st.title("Lideranças Empáticas")
    st.caption("Gestão de grupos e arrecadações")

st.divider()

# 1. Inicializa o estado da sessão para dados e para a CÂMERA
if "itens_salvos" not in st.session_state:
    st.session_state.itens_salvos = []
if "contagem_atual" not in st.session_state:
    st.session_state.contagem_atual = []
if "camera" not in st.session_state:
    st.session_state.camera = None
if "ultimo_frame" not in st.session_state:
    st.session_state.ultimo_frame = None


# Logica de envio
def enviar(dadosenviar):
    payload = {
        "idGrupo": grupo,
        "nome": cookies['nome'],
        "dados": dadosenviar
    }
    response = requests.post(apiURL + "/captura", json=payload)

    if response.status_code == 200:
        st.success("Dados enviados com sucesso!")
        st.session_state["itens_salvos"] = []
        st.rerun()
    else:
        st.error("Erro ao enviar dados.\n" + response.text)

url = buscarURL()+"/uploads/modelo/best.pt"
# 2. Carrega o modelo
@st.cache_resource
def load_model():
    return YOLO(
        "./best.pt")


modelo = load_model()

st.title("Captura com Detecção")

# 3. Controles
run = st.checkbox("Ligar câmera")
capturar = shortcut_button(
    "Capturar Itens",
    shortcut="Enter"
)

# 6. Layout para o vídeo ao vivo
col1, col2 = st.columns(2)
frame_placeholder = col1.empty()
table_placeholder = col2.empty()

# 4. Lógica do Botão: Atualiza os dados salvos associando o frame ao clique
if capturar:
    if st.session_state.ultimo_frame is not None:
        # Converte o último frame capturado para uma string Base64
        img = Image.fromarray(st.session_state.ultimo_frame)
        buffered = BytesIO()
        img.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        img_data_uri = f"data:image/jpeg;base64,{img_str}"

        # Adiciona a imagem a cada item detectado naquele momento
        itens_com_imagem = []
        for item in st.session_state.contagem_atual:
            novo_item = item.copy()
            novo_item["Frame"] = img_data_uri
            itens_com_imagem.append(novo_item)

        st.session_state.itens_salvos.extend(itens_com_imagem)
    else:
        st.session_state.itens_salvos.extend(st.session_state.contagem_atual)


st.divider()

# 5. Renderiza os Itens Salvos com a Coluna de Imagem
st.subheader("Itens Capturados (Salvos)")
if st.session_state.itens_salvos:
    # Usando st.column_config para renderizar o Base64 como imagem na tabela
    dados = st.data_editor(
        st.session_state.itens_salvos,
        column_config={
            "Frame": st.column_config.ImageColumn(
                "Imagem", help="Frame capturado da câmera"
            )
        },
        hide_index=True
    )
    if not run:
        coltab1, coltab2 = st.columns(2)
        with coltab1:
            enviarDados = st.button("Enviar")
            if enviarDados:
                enviar(dados)
        with coltab2:
            # Botão para limpar tabela
            if st.session_state.itens_salvos:
                if st.button("Limpar Tabela"):
                    st.session_state.itens_salvos = []
                    st.rerun()
    else:
        st.warning("Para enviar os dados desligue a câmera")
else:
    st.info("Clique em 'Capturar Itens' enquanto a câmera estiver ligada para registrar os itens.")

# 7. Loop de Vídeo Protegido
if run:
    if st.session_state.camera is None:
        st.session_state.camera = cv2.VideoCapture(buscarVideoURL())

    while True:
        sucesso, frame = st.session_state.camera.read()
        if not sucesso:
            st.error("Erro ao acessar a câmera!")
            break

        resultados = list(modelo(frame, stream=True, conf=0.5))
        itens_frame = []

        frame_anotado = frame.copy()

        for resultado in resultados:
            frame_anotado = resultado.plot().copy()

            nomes = resultado.names

            for box in resultado.boxes:
                cls_id = int(box.cls[0])
                nome_item = nomes[cls_id]

                itens_frame.append(nome_item)

                # =========================
                # Coordenadas da detecção
                # =========================
                x1, y1, x2, y2 = box.xyxy[0].tolist()

                # =========================
                # MEDIÇÃO EM CM
                # =========================
                base_esq_pixel = np.array([[[x1, y2]]], dtype="float32")
                base_dir_pixel = np.array([[[x2, y2]]], dtype="float32")

                base_esq_cm = cv2.perspectiveTransform(
                    base_esq_pixel,
                    matriz_medidas
                )[0][0]

                base_dir_cm = cv2.perspectiveTransform(
                    base_dir_pixel,
                    matriz_medidas
                )[0][0]

                largura_cm = math.sqrt(
                    (base_dir_cm[0] - base_esq_cm[0]) ** 2 +
                    (base_dir_cm[1] - base_esq_cm[1]) ** 2
                )

                # =========================
                # DESENHO VISUAL
                # =========================
                cv2.line(
                    frame_anotado,
                    (int(x1), int(y2)),
                    (int(x2), int(y2)),
                    (0, 255, 255),
                    3
                )

                texto_medida = f"{largura_cm:.1f}"

                cv2.putText(
                    frame_anotado,
                    texto_medida,
                    (int(x1), int(y1) - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 255),
                    2
                )

        contagem = Counter(itens_frame)

        # Desenha Overlay
        y_pos = 40
        cv2.rectangle(frame_anotado, (10, 10), (350, 150), (0, 0, 0), -1)

        for item, quantidade in contagem.items():
            texto = f"{item}: {quantidade}"
            cv2.putText(frame_anotado, texto, (20, y_pos),
                        cv2.FONT_HERSHEY_COMPLEX, 0.8,
                        (255, 255, 255), 2)
            y_pos += 30

        # Converte BGR → RGB
        frame_anotado = cv2.cvtColor(frame_anotado, cv2.COLOR_BGR2RGB)

        # SALVA O FRAME ATUAL PARA O BOTÃO CAPTURAR
        st.session_state.ultimo_frame = frame_anotado

        # Atualiza as colunas
        frame_placeholder.image(frame_anotado, channels="RGB")

        # Prepara a contagem (deixando o espaço de "Frame" vazio durante o ao vivo)
        tabela = []

        for resultado in resultados:
            nomes = resultado.names

            for box in resultado.boxes:
                cls_id = int(box.cls[0])
                nome_item = nomes[cls_id]

                x1, y1, x2, y2 = box.xyxy[0].tolist()

                # Conversão pixel -> cm
                base_esq_pixel = np.array([[[x1, y2]]], dtype="float32")
                base_dir_pixel = np.array([[[x2, y2]]], dtype="float32")

                base_esq_cm = cv2.perspectiveTransform(
                    base_esq_pixel,
                    matriz_medidas
                )[0][0]

                base_dir_cm = cv2.perspectiveTransform(
                    base_dir_pixel,
                    matriz_medidas
                )[0][0]

                largura_cm = math.sqrt(
                    (base_dir_cm[0] - base_esq_cm[0]) ** 2 +
                    (base_dir_cm[1] - base_esq_cm[1]) ** 2
                )
                pesoAtual = 0
                if nome_item == "Pacote de Arroz" and largura_cm > 30:
                    pesoAtual = 5
                elif nome_item == "Pacote de Arroz" and largura_cm <= 15:
                    pesoAtual = 1
                elif nome_item == "Pacote de Arroz":
                    pesoAtual = 2
                elif nome_item == "Oleo de Soja" or nome_item == "Fuba" or nome_item == "Cafe" or nome_item == "Macarrao" or nome_item == "Macarrao Espaguete":
                    pesoAtual = 0.5
                elif nome_item == "Acucar" or nome_item == "Feijao Carioca":
                    pesoAtual = 1

                confianca = float(box.conf[0])
                tabela.append({
                    "Item": nome_item,
                    "Quantidade": 1,
                    "Marca": "",
                    "Peso": f"{pesoAtual:.1f}",
                    "Data": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Confianca": confianca
                })
        st.session_state.contagem_atual = tabela

        if tabela:
            table_placeholder.table(tabela)
        else:
            table_placeholder.write("Nenhum item detectado...")

else:
    if st.session_state.camera is not None:
        st.session_state.camera.release()
        st.session_state.camera = None

    frame_placeholder.write("Câmera desligada.")
    table_placeholder.empty()
