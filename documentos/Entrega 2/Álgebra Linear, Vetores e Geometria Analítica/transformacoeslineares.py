import numpy as np
from PIL import Image
import csv

print("Lendo os dados do arquivo CSV original...")

# 1. Lendo os dados espaciais e de cor do CSV original
with open("pixels.csv", "r") as f:
    reader = list(csv.reader(f))

# Separa o cabeçalho dos dados
header = reader[0]
data = reader[1:]

height = len(data)
width = len(header) // 3  # Cada pixel ocupa 3 colunas (R, G, B)

# 2. Definição explícita da matriz de transformação (Cisalhamento)
k = 0.5
matriz_transformacao = np.array([
    [1, k],
    [0, 1]
])

# Calcula as novas dimensões para evitar cortes
nova_largura = int(width + (height * k))
nova_altura = height

# 3. Preparando as estruturas para os dois outputs (Imagem e CSV)

# A) Cria a nova imagem vazia (fundo preto)
nova_img = Image.new("RGB", (nova_largura, nova_altura), "black")
novos_pixels = nova_img.load()

# B) Cria a nova matriz de dados para o CSV (preenchida com zeros/preto)
# Uma lista de listas, onde cada linha tem (nova_largura * 3) colunas
nova_matriz_csv = [[0 for _ in range(nova_largura * 3)] for _ in range(nova_altura)]

print("Aplicando a transformação linear...")

# 4. Aplicação da matriz às coordenadas
for y, row in enumerate(data):
    for x in range(width):
        # Extrai os valores RGB do pixel original a partir do CSV
        r = int(row[x * 3])
        g = int(row[x * 3 + 1])
        b = int(row[x * 3 + 2])

        # Vetor de coordenadas espaciais originais
        v = np.array([x, y])

        # Multiplicação de matriz: v_novo = Matriz * v
        v_novo = matriz_transformacao.dot(v)

        novo_x = int(v_novo[0])
        novo_y = int(v_novo[1])

        # Verifica os limites para não dar erro de "out of bounds"
        if 0 <= novo_x < nova_largura and 0 <= novo_y < nova_altura:
            # 1º Output: Atualiza o pixel na nova imagem
            novos_pixels[novo_x, novo_y] = (r, g, b)

            # 2º Output: Atualiza os valores R, G e B na nova matriz CSV
            # Como cada pixel ocupa 3 posições, multiplicamos o x por 3
            nova_matriz_csv[novo_y][novo_x * 3]     = r
            nova_matriz_csv[novo_y][novo_x * 3 + 1] = g
            nova_matriz_csv[novo_y][novo_x * 3 + 2] = b

# 5. Salvando os resultados

# Salva a imagem visual
nova_img.save("imagem_transformada.png")

# Salva a nova matriz no arquivo CSV
print("Gerando o novo arquivo CSV...")
with open("pixels_transformados.csv", "w", newline="") as f:
    writer = csv.writer(f)

    # Cria o novo cabeçalho (agora indo até a nova_largura)
    novo_header = []
    for x in range(1, nova_largura + 1):
        novo_header.extend([f"r{x}", f"g{x}", f"b{x}"])
    writer.writerow(novo_header)

    # Escreve as novas linhas de dados
    for row in nova_matriz_csv:
        writer.writerow(row)

nova_img.show()
print("Sucesso!")
print("- Imagem salva como: 'imagem_transformada.png'")
print("- Matriz salva como: 'pixels_transformados.csv'")
