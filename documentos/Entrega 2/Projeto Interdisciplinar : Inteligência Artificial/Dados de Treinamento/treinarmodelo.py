import os
import yaml
from ultralytics import YOLO

base_path = "./DadosRotulados"

train_images = os.path.join(base_path, "images/Train")
val_images = os.path.join(base_path, "images/Validation")

caminho_yaml = os.path.join(base_path, "data.yaml")

# Load YAML
with open(caminho_yaml, "r") as f:
    dados = yaml.safe_load(f)

# Update paths
dados['train'] = train_images
dados['val'] = val_images

if 'test' in dados:
    dados['test'] = val_images

# Save YAML
with open(caminho_yaml, 'w') as f:
    yaml.dump(dados, f)

# Train model
model = YOLO('yolov8n.pt')

resultados = model.train(
    data=caminho_yaml,
    epochs=50,
    imgsz=640
)

arquivo_final = './runs/detect/train/weights/best.pt'
