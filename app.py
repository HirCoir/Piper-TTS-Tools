import importlib.util
import subprocess
import sys
import shlex

def verify_and_install_lib(lib_name):
    """
    Verifica la existencia de una biblioteca en Python y ejecuta "pip install" si no está presente.
    :param lib_name: nombre de la biblioteca.
    :return: True si la biblioteca se encontró o se instaló correctamente.
    """
    has_lib = importlib.util.find_spec(lib_name) is not None
    if not has_lib:
        print(f"La biblioteca {lib_name} no se encontró. Instalándola...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", lib_name])
    return has_lib

# Lista de bibliotecas a verificar y instalar si no están presentes
libs_to_install = [
    "logging",
    "flask",
    "art",
    "colorlog",
    "tqdm"
]

# Ejecuta la verificación e instalación de cada biblioteca
for lib in libs_to_install:
    verify_and_install_lib(lib)



import os
import zipfile
from urllib.request import urlretrieve
from tqdm import tqdm

class DownloadProgressBar(tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)

def verificar_y_descomprimir_piper():
    """
    Verifica si existe la carpeta 'piper'. Si no existe, intenta descomprimir el archivo 'piper_windows_amd64.zip'.
    Si el archivo tampoco existe, lo descarga desde la URL especificada con una barra de progreso y luego lo descomprime.
    """
    piper_carpeta = "piper"
    piper_archivo = "piper_windows_amd64.zip"
    piper_url = "https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_windows_amd64.zip"

    if not os.path.exists(piper_carpeta):
        print("Carpeta 'piper' no encontrada.")
        if os.path.exists(piper_archivo):
            print("Descomprimiendo archivo 'piper_windows_amd64.zip'...")
            with zipfile.ZipFile(piper_archivo, 'r') as zip_ref:
                zip_ref.extractall()
        else:
            print("Descargando 'piper_windows_amd64.zip'...")
            with DownloadProgressBar(unit='B', unit_scale=True, miniters=1, desc=piper_archivo) as t:
                urlretrieve(piper_url, piper_archivo, reporthook=t.update_to)
            print("Descomprimiendo archivo 'piper_windows_amd64.zip'...")
            with zipfile.ZipFile(piper_archivo, 'r') as zip_ref:
                zip_ref.extractall()
    else:
        print("Carpeta 'piper' ya existe.")

if __name__ == "__main__":
    verificar_y_descomprimir_piper()
    
import os
import zipfile
from urllib.request import urlretrieve
from tqdm import tqdm
import logging
from flask import Flask, render_template, request, jsonify, after_this_request, send_from_directory, abort
from functools import wraps
from io import BytesIO
import base64
import subprocess
import random
import string
import re
import sys
import webbrowser
from art import text2art
import colorlog
from colorlog import ColoredFormatter
import tkinter as tk
from tkinter import filedialog
import shlex

class DownloadProgressBar(tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)

def verificar_y_descomprimir_piper():
    """
    Verifica si existe la carpeta 'piper'. Si no existe, intenta descomprimir el archivo 'piper_windows_amd64.zip'.
    Si el archivo tampoco existe, lo descarga desde la URL especificada con una barra de progreso y luego lo descomprime.
    """
    piper_carpeta = "piper"
    piper_archivo = "piper_windows_amd64.zip"
    piper_url = "https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_windows_amd64.zip"

    if not os.path.exists(piper_carpeta):
        print("Carpeta 'piper' no encontrada.")
        if os.path.exists(piper_archivo):
            print("Descomprimiendo archivo 'piper_windows_amd64.zip'...")
            with zipfile.ZipFile(piper_archivo, 'r') as zip_ref:
                zip_ref.extractall()
        else:
            print("Descargando 'piper_windows_amd64.zip'...")
            with DownloadProgressBar(unit='B', unit_scale=True, miniters=1, desc=piper_archivo) as t:
                urlretrieve(piper_url, piper_archivo, reporthook=t.update_to)
            print("Descomprimiendo archivo 'piper_windows_amd64.zip'...")
            with zipfile.ZipFile(piper_archivo, 'r') as zip_ref:
                zip_ref.extractall()
    else:
        print("Carpeta 'piper' ya existe.")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = ColoredFormatter(
    "%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s",
    datefmt=None,
    reset=True,
    log_colors={
        'DEBUG': 'purple',
        'INFO': 'cyan',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'white,bg_red',
    }
)
handler.setFormatter(formatter)
logger.addHandler(handler)

def print_ascii_name(name):
    ascii_name = text2art(name)
    print(ascii_name)

print_ascii_name("HirCoir")
app = Flask(__name__)

file_folder = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
temp_audio_folder = os.path.join(file_folder, 'temp_audio')
piper_binary_path = os.path.join(file_folder, 'piper', 'piper.exe')

def filter_text(text):
    filtered_text = shlex.quote(text)  # Utiliza shlex para eliminar caracteres especiales
    filtered_text = filtered_text.replace('\n', ' ')
    return filtered_text

def convert_text_to_speech(text, model, model_folder):
    filtered_text = filter_text(text)
    random_name = ''.join(random.choices(string.ascii_letters + string.digits, k=8)) + '.wav'
    output_file = os.path.join(temp_audio_folder, random_name)
    model_path = os.path.join(model_folder, model)

    if os.path.isfile(piper_binary_path) and os.path.isfile(model_path):
        command = f'echo "{filtered_text}" | "{piper_binary_path}" -m {model_path} -f {output_file}'
        try:
            subprocess.run(command, shell=True, check=True)
            return output_file
        except subprocess.CalledProcessError as e:
            logging.error(f"Error al ejecutar el comando: {e}")

    return None

def restrict_access(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        referer = request.headers.get("Referer")
        if referer and referer.endswith("/"):
            return func(*args, **kwargs)
        else:
            return abort(403)
    return wrapper

def select_model_folder():
    root = tk.Tk()
    root.withdraw()
    folder_selected = filedialog.askdirectory()
    return folder_selected if folder_selected else None

def start_flask_server():
    model_folder = select_model_folder()
    if model_folder:
        logging.info("Se ha seleccionado la carpeta de modelos: %s", model_folder)
        webbrowser.open_new_tab("http://127.0.0.1:7860/")
        app.model_folder = model_folder  # Guardar model_folder en app
        app.run(host='127.0.0.1', port=7860, debug=False)
    else:
        logging.error("No se pudo iniciar el servidor Flask debido a que no se seleccionó una carpeta de modelos.")

@app.route('/')
def index():
    model_options = [file for file in os.listdir(app.model_folder) if file.endswith('.onnx')]
    return render_template('index.html', model_options=model_options)
    
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'templates'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/image.jpg')
def image():
    return send_from_directory(os.path.join(app.root_path, 'templates'), 'image.jpg', mimetype='image/jpeg')

@app.route('/convert', methods=['POST'])
@restrict_access
def convert_text():
    text = request.form['text']
    model = request.form['model']
    output_file = convert_text_to_speech(text, model, app.model_folder)

    @after_this_request
    def remove_file(response):
        try:
            os.remove(output_file)
            logging.info("Audio file deleted: %s", output_file)
        except Exception as error:
            logging.error("Error deleting file: %s", error)
        return response

    if output_file is not None:
        with open(output_file, 'rb') as audio_file:
            audio_content = audio_file.read()
        audio_base64 = base64.b64encode(audio_content).decode('utf-8')
        response = jsonify({'audio_base64': audio_base64})
    else:
        response = jsonify({'error': 'Error al convertir texto a voz'})

    return response

if __name__ == '__main__':
    logging.info("Se está iniciando la aplicación.")
    start_flask_server()
