from PIL import Image
import csv

img = Image.open("alimentos.jpg").convert("RGB")
width, height = img.size
pixels = img.load()

with open("pixels.csv", "w", newline="") as f:
    writer = csv.writer(f)

    header = []
    for x in range(1, width + 1):
        header.extend([f"r{x}", f"g{x}", f"b{x}"])
    writer.writerow(header)

    for y in range(height):
        row = []
        for x in range(width):
            r, g, b = pixels[x, y]
            row.extend([r, g, b])  # adiciona 3 colunas por pixel
        writer.writerow(row)