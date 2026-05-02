import numpy as np
from PIL import Image

# 1. Carrega a imagem original
img = Image.open("alimentos.jpg").convert("RGB")

width, height = img.size
pixels = img.load()

# 2. Definição explícita da matriz de transformação
# Fator de cisalhamento
k = 0.5
# É possivel transformar a matriz verticalmente ou horizontalmente mudando a posição do k
matriz_transformacao = np.array([
    [1, k],
    [0, 1]
])

# Para evitar que a imagem saia cortada, calculamos a nova largura aproximada
nova_largura = int(width + (height * k))
nova_altura = height #Cisalhamento Vertical = (height + (width * k))

# Cria a nova imagem (fundo preto)
nova_img = Image.new("RGB", (nova_largura, nova_altura), "black")
novos_pixels = nova_img.load()

# 3. Aplicação da matriz às coordenadas dos pixels
for y in range(height):
    for x in range(width):
        # Vetor de coordenadas espaciais originais
        v = np.array([x, y])

        # Multiplicação de matriz: v_novo = Matriz * v
        v_novo = matriz_transformacao.dot(v)

        novo_x = int(v_novo[0])
        novo_y = int(v_novo[1])

        # Verifica os limites para não dar erro de "out of bounds"
        if 0 <= novo_x < nova_largura and 0 <= novo_y < nova_altura:
            novos_pixels[novo_x, novo_y] = pixels[x, y]

# 4. Salva e exibe a visualização da imagem transformada
nova_img.save("imagem_transformada.png")
nova_img.show()
print("Transformação concluída e salva como 'imagem_transformada.png'")