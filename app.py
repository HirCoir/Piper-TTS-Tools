import logging
import os
import random
import re
import string
import subprocess
import time
import base64
import tkinter as tk
from tkinter import filedialog
from flask import Flask, request, jsonify, send_from_directory
from functools import wraps

# Configuración del registro
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# Define el directorio donde se guardan los archivos
file_folder = os.path.dirname(os.path.abspath(__file__))  # Obtiene la ruta del directorio actual del archivo
temp_audio_folder = os.path.join(file_folder, 'temp_audio')
model_folder = None
piper_binary_path = os.path.join(file_folder, 'piper', 'piper.exe')  # Cambia la ruta al ejecutable de piper.exe en Windows

# Crea la carpeta temp_audio si no existe
os.makedirs(temp_audio_folder, exist_ok=True)

# Ajuste global para los reemplazos en el texto
global_replacements = [('\n', ' . '), ('*', '')]

def multiple_replace(text, replacements):
    # Iterar sobre cada par de remplazo
    for old, new in replacements:
        text = text.replace(old, new)
    return text

def filter_text(text):
    # Realizar reemplazos globales en el texto
    filtered_text = multiple_replace(text, global_replacements)
    # Escapar todos los caracteres especiales dentro de las comillas
    filtered_text = re.sub(r'(["\'])', lambda m: "\\" + m.group(0), filtered_text)
    return filtered_text

def convert_text_to_speech(text, model_name):
    filtered_text = filter_text(text)[:3000]  # Limitar el texto a 3000 caracteres
    if filtered_text is None:
        return None

    random_name = ''.join(random.choices(string.ascii_letters + string.digits, k=8)) + '.wav'
    output_file = os.path.join(temp_audio_folder, random_name)

    if os.path.isfile(piper_binary_path) and model_folder is not None:
        model_path = os.path.join(model_folder, model_name)
        if os.path.isfile(model_path):
            # Construye el comando para ejecutar Piper
            command = f'echo "{filtered_text}" | "{piper_binary_path}" -m "{model_path}" -f "{output_file}"'  # Rutas entre comillas dobles
            try:
                subprocess.run(command, shell=True, check=True)
                return output_file
            except subprocess.CalledProcessError as e:
                logging.error(f"Error al ejecutar el comando: {e}")
                return None
        else:
            logging.error(f"Modelo '{model_name}' no encontrado en la ubicación especificada.")
            return None
    else:
        logging.error(f"No se encontró el binario de Piper en la ubicación especificada o no se ha seleccionado una carpeta de modelos.")
        return None

def rate_limit(limit):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not hasattr(wrapper, 'last_execution'):
                wrapper.last_execution = 0
            elapsed_time = time.time() - wrapper.last_execution
            if elapsed_time < limit:
                return jsonify({'error': 'Demasiadas solicitudes. Por favor, inténtalo de nuevo más tarde.'}), 429
            wrapper.last_execution = time.time()
            return func(*args, **kwargs)
        return wrapper
    return decorator

def select_model_folder():
    global model_folder
    root = tk.Tk()
    root.withdraw()
    model_folder = filedialog.askdirectory()

@app.route('/convert', methods=['POST'])
@rate_limit(1)  # Limita las solicitudes a 1 por segundo
def convert_text():
    data = request.json
    text = data.get('text')
    model_name = data.get('model')
    output_file = convert_text_to_speech(text, model_name)

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

@app.route('/models', methods=['GET'])
def list_models():
    if model_folder is not None:
        model_options = [model_name for model_name in os.listdir(model_folder) if model_name.endswith('.onnx')]
        return jsonify({'models': model_options})
    else:
        return jsonify({'error': 'No se ha seleccionado una carpeta de modelos'}), 500
@app.route('/examples', methods=['GET'])
def examples():
    return send_from_directory(file_folder, 'examples.html')

@app.route('/help', methods=['GET'])
def help_page():
    return send_from_directory(file_folder, 'examples.html')

@app.route('/ejemplos', methods=['GET'])
def ejemplos():
    return send_from_directory(file_folder, 'ejemplos.html')

@app.route('/ayuda', methods=['GET'])
def ayuda():
    return send_from_directory(file_folder, 'ejemplos.html')

if __name__ == '__main__':
    logging.info("Se está iniciando la aplicación.")
    select_model_folder()
    # Abre el navegador automáticamente con la página
    app.run(host='localhost', port=8080, debug=False)