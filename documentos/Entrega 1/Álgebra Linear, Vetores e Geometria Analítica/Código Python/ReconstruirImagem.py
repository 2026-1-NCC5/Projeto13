from PIL import Image
import csv

with open("pixels.csv", "r") as f:
    reader = list(csv.reader(f))

# remove o cabeçalho
header = reader[0]
data = reader[1:]

height = len(data)
width = len(header) // 3  # cada pixel ocupa 3 colunas

# cria imagem vazia
img = Image.new("RGB", (width, height))
pixels = img.load()

for y, row in enumerate(data):
    for x in range(width):
        r = int(row[x * 3])
        g = int(row[x * 3 + 1])
        b = int(row[x * 3 + 2])
        pixels[x, y] = (r, g, b)

img.save("reconstruida.png")