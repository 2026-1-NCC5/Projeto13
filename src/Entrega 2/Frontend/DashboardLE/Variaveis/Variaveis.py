from dotenv import load_dotenv
import os

load_dotenv()

def buscarURL():
    return os.getenv("API_URL")

def buscarChave():
    return os.getenv("SECRET_KEY")

def buscarVideoURL():
    return os.getenv("VIDEO_URL")