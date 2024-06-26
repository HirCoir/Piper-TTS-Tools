import logging
from flask import Flask, render_template, request, jsonify, after_this_request, send_from_directory
from functools import wraps
from io import BytesIO
import base64
import subprocess
import os
import random
import string
import re
import sys
import time
# Configuración del registro
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# Define el directorio donde se guardan los archivos
file_folder = '/home/app'
temp_audio_folder = os.path.join(file_folder, 'temp_audio')
model_folder = os.path.join(file_folder, 'models')
piper_binary_path = os.path.join(file_folder, 'piper', 'piper')

# Crea la carpeta temp_audio si no existe
if not os.path.exists(temp_audio_folder):
    os.makedirs(temp_audio_folder)

# Define los nombres asignados a modelos específicos
model_names = {
    "Español México    | Claude": "es_MX-claude-14947-epoch-high.onnx",
    "Español México    |  Cortana v1": "es_MX-cortana-19669-epoch-high.onnx",
    "Español México    |  Cortana v3": "es_MX-cortanav3-17139-high.onnx",
    "Español México    |  Ald (Medium)": "es_MX-ald-medium.onnx",
    "Español Argentina |  Microsoft Elena": "es_MX-hircoirvoicev5-high.onnx",
    "Español México    |  Hircoir v1": "es_MX-locutor-18488-epoch-high.onnx",
# Modelos públicos de huggingface
    "Español España    |  Carlfm (Low)": "es_ES-carlfm-x_low.onnx",
    "Español España    |  Davefx (Medium)": "es_ES-davefx-medium.onnx",
    "Español España    |  Mls 9972 (Low)": "es_ES-mls_9972-low.onnx",
    "Español Españá    |  Mls 10246 (Low)": "es_ES-mls_10246-low.onnx",
    "Español España    |  Sharvard (Medium)": "es_ES-sharvard-medium.onnx",
    "English US    |  Lessac (High)": "en_US-lessac-high.onnx",
    "English US    |  Amy (Medium)": "en_US-amy-medium.onnx",
    "English US    |  Dany (Low)": "en_US-danny-low.onnx",
    "English US    |  HFC Male": "en_US-hfc_male-medium.onnx",
    "English US    |  Kusal (Medium)": "en_US-kusal-medium.onnx",
    "English US    |  Joe (Medium)": "en_US-joe-medium.onnx",
    "English US    |  12Arctic (Medium)": "en_US-l2arctic-medium.onnx",
    "English US    |  LibriTTS (High)": "en_US-libritts-high.onnx"
}

def multiple_replace(text, replacements):
    # Iterar sobre cada par de remplazo
    for old, new in replacements:
        text = text.replace(old, new)
    return text

def filter_text(text):
    # Lista de remplazos a realizar
    replacements = [('(', ','), (')', ','), ('?', ','), ('¿', ','), (':', ','), ('\n', ' ')]
    
    # Realizar remplazos
    filtered_text = multiple_replace(text, replacements)
    
    # Escapar todos los caracteres especiales dentro de las comillas
    filtered_text = re.sub(r'(["\'])', lambda m: "\\" + m.group(0), filtered_text)
    
    return filtered_text

# Define una función para convertir texto a voz
def convert_text_to_speech(text, model):
    filtered_text = filter_text(text)
    random_name = ''.join(random.choices(string.ascii_letters + string.digits, k=8)) + '.wav'
    output_file = os.path.join(temp_audio_folder, random_name)

    if os.path.isfile(piper_binary_path):
        if model in model_names:
            model_path = os.path.join(model_folder, model_names[model])
            if os.path.isfile(model_path):
                # Construye el comando para ejecutar Piper
                command = f'echo "{filtered_text}" | "{piper_binary_path}" -m {model_path} -f {output_file}'
                try:
                    subprocess.run(command, shell=True, check=True)
                    return output_file
                except subprocess.CalledProcessError as e:
                    logging.error(f"Error al ejecutar el comando: {e}")
                    return None
            else:
                logging.error(f"Modelo '{model}' no encontrado en la ubicación especificada.")
                return None
        else:
            logging.error(f"No se ha asignado un modelo para el nombre '{model}'.")
            return None
    else:
        logging.error(f"No se encontró el binario de Piper en la ubicación especificada.")
        return None

# Define una función decoradora para limitar la velocidad de las solicitudes
def rate_limit(limit):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not hasattr(wrapper, 'last_execution'):
                wrapper.last_execution = 0
            elapsed_time = time.time() - wrapper.last_execution
            if elapsed_time < limit:
                return jsonify({'error': 'Too many requests. Please try again later.'}), 429
            wrapper.last_execution = time.time()
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Define una función decoradora para restringir el acceso a la ruta /convert
def restrict_access(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Verifica si la solicitud se hizo desde la página index.html
        referer = request.headers.get("Referer")
        if referer and referer.endswith("/"):
            # Permite el acceso a la función si la solicitud proviene de la página index.html
            return func(*args, **kwargs)
        else:
            # Devuelve un mensaje de error o redirecciona a otra página
            return "Acceso no autorizado", 403  # Código de respuesta HTTP 403 - Forbidden
    return wrapper

@app.route('/')
def index():
    model_options = [name for name, model in model_names.items() if os.path.isfile(os.path.join(model_folder, model))]
    # Registra el contenido de la carpeta actual
    logging.info("Contents of current folder: %s", os.listdir(file_folder))
    return render_template('index.html', model_options=model_options)

@app.route('/convert', methods=['POST'])
@restrict_access
@rate_limit(1)  # Limita las solicitudes a 1 por segundo
def convert_text():
    text = request.form['text']
    model = request.form['model']
    output_file = convert_text_to_speech(text, model)

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

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'templates'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/image.jpg')
def image():
    return send_from_directory(os.path.join(app.root_path, 'templates'), 'image.jpg', mimetype='image/jpeg')

if __name__ == '__main__':
    logging.info("Se está iniciando la aplicación.")
    app.run(host='0.0.0.0', port=7860, debug=False)
