import cv2
from ultralytics import YOLO
from collections import Counter

#Alvos: Arroz, Feijão Carioca e Óleo de Soja

modelo=YOLO('best.pt')

camera = cv2.VideoCapture("http://192.168.1.101:4747/video")

print("Iniciando a câmera... Pressione q para sair.")

while True:
    sucesso, frame = camera.read()
    if not sucesso:
        print("Erro ao acessar a câmera!")
        break
    resultados = modelo(frame, stream=True)
    itens_frame = []
    frame_anotado = frame

    for resultado in resultados:
        frame_anotado = resultado.plot().copy()
        classes_ids = resultado.boxes.cls.tolist()
        nomes = resultado.names
        for cls_id in classes_ids:
            itens_frame.append(nomes[int(cls_id)])
    contagem = Counter(itens_frame)
    y_pos = 40
    cv2.rectangle(frame_anotado, (10,10), (350,150), (0,0,0), -1)

    for item, quantidade in contagem.items():
        texto_contagem = f"{item}: {quantidade} unidade"
        cv2.putText(frame_anotado, texto_contagem, (20, y_pos), cv2.FONT_HERSHEY_COMPLEX, 0.8, (255,255,255), 2)
        y_pos += 30
    
    cv2.imshow("Contador de items", frame_anotado)
    if(cv2.waitKey(1) & 0xFF == ord('q')):
        break
camera.release()
cv2.destroyAllWindows()