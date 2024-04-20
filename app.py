import logging
import os
import random
import re
import string
import subprocess
import time
import base64

from flask import Flask, render_template, request, jsonify, after_this_request, send_from_directory
from functools import wraps

# Configuración del registro
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# Define el directorio donde se guardan los archivos
file_folder = '/home/app'
temp_audio_folder = os.path.join(file_folder, 'temp_audio')
model_folder = os.path.join(file_folder, 'models')
piper_binary_path = os.path.join(file_folder, 'piper', 'piper')

# Crea la carpeta temp_audio si no existe
os.makedirs(temp_audio_folder, exist_ok=True)

# Define los nombres asignados a modelos específicos, en caso de no existir no se muestran
model_names = {
    "Español México | Sorah Neuronal": {
        "model_path": "es_MX-sorah-high.onnx",
        "replacements": [('\n', ''), ('*', '')]
    },
    "Español México | Emma Neuronal": {
        "model_path": "es_MX-emma-high.onnx",
        "replacements": [('\n', ''), ('*', '')]
    },
    "Español México | Kamora Neuronal": {
        "model_path": "kamora.onnx",
        "replacements": [('\n', ''), ('*', '')]
    },
    "Español México | Voz HirCoir": {
        "model_path": "es_MX-locutor-18488-epoch-high.onnx",
        "replacements": [('(', ','), (')', ','), ('?', ','), ('¿', ','), (':', ','), ('\n', ' ')]
    },
    "Español México    | Claude": {
        "model_path": "es_MX-claude-14947-epoch-high.onnx",
        "replacements": [('(', ','), (')', ','), ('?', ','), ('¿', ','), (':', ','), ('\n', ' ')]
    },
    "Español México    | Cortana Infinite": {
        "model_path": "es_MX-cortana-26284-high.onnx",
        "replacements": [('(', ','), (')', ','), ('?', ','), ('¿', ','), (':', ','), ('\n', ' ')]
    },
    "Español México    | Ald (Medium)": {
        "model_path": "es_MX-ald-medium.onnx",
        "replacements": [('(', ','), (')', ','), ('?', ','), ('¿', ','), (':', ','), ('\n', ' ')]
    },
    "Español Argentina | Microsoft Elena": {
        "model_path": "es_MX-hircoirvoicev5-high.onnx",
        "replacements": [('(', ','), (')', ','), ('?', ','), ('¿', ','), (':', ','), ('\n', ' ')]
    },
    "Español México    | Hircoir v1": {
        "model_path": "es_MX-locutor-18488-epoch-high.onnx",
        "replacements": [('(', ','), (')', ','), ('?', ','), ('¿', ','), (':', ','), ('\n', ' ')]
    },
    "Español España    | Carlfm (Low)": {
        "model_path": "es_ES-carlfm-x_low.onnx",
        "replacements": [('(', ','), (')', ','), ('?', ','), ('¿', ','), (':', ','), ('\n', ' ')]
    },
    "Español España    | Davefx (Medium)": {
        "model_path": "es_ES-davefx-medium.onnx",
        "replacements": [('(', ','), (')', ','), ('?', ','), ('¿', ','), (':', ','), ('\n', ' ')]
    },
    "Español España    | Mls 9972 (Low)": {
        "model_path": "es_ES-mls_9972-low.onnx",
        "replacements": [('(', ','), (')', ','), ('?', ','), ('¿', ','), (':', ','), ('\n', ' ')]
    },
    "Español Españá    | Mls 10246 (Low)": {
        "model_path": "es_ES-mls_10246-low.onnx",
        "replacements": [('(', ','), (')', ','), ('?', ','), ('¿', ','), (':', ','), ('\n', ' ')]
    },
    "Español España    | Sharvard (Medium)": {
        "model_path": "es_ES-sharvard-medium.onnx",
        "replacements": [('(', ','), (')', ','), ('?', ','), ('¿', ','), (':', ','), ('\n', ' ')]
    },
    "English US    | Lessac (High)": {
        "model_path": "en_US-lessac-high.onnx",
        "replacements": [('(', ','), (')', ','), ('?', ','), ('¿', ','), (':', ','), ('\n', ' ')]
    },
    "English US    | Amy (Medium)": {
        "model_path": "en_US-amy-medium.onnx",
        "replacements": [('(', ','), (')', ','), ('?', ','), ('¿', ','), (':', ','), ('\n', ' ')]
    },
    "English US    | Dany (Low)": {
        "model_path": "en_US-danny-low.onnx",
        "replacements": [('(', ','), (')', ','), ('?', ','), ('¿', ','), (':', ','), ('\n', ' ')]
    },
    "English US    | HFC Male": {
        "model_path": "en_US-hfc_male-medium.onnx",
        "replacements": [('(', ','), (')', ','), ('?', ','), ('¿', ','), (':', ','), ('\n', ' ')]
    },
    "English US    | Kusal (Medium)": {
        "model_path": "en_US-kusal-medium.onnx",
        "replacements": [('(', ','), (')', ','), ('?', ','), ('¿', ','), (':', ','), ('\n', ' ')]
    },
    "English US    | Joe (Medium)": {
        "model_path": "en_US-joe-medium.onnx",
        "replacements": [('(', ','), (')', ','), ('?', ','), ('¿', ','), (':', ','), ('\n', ' ')]
    },
    "English US    | 12Arctic (Medium)": {
        "model_path": "en_US-l2arctic-medium.onnx",
        "replacements": [('(', ','), (')', ','), ('?', ','), ('¿', ','), (':', ','), ('\n', ' ')]
    },
    "English US    | LibriTTS (High)": {
        "model_path": "en_US-libritts-high.onnx",
        "replacements": [('(', ','), (')', ','), ('?', ','), ('¿', ','), (':', ','), ('\n', ' ')]
    }
}
# Comprueba si los modelos definidos existen en la carpeta de modelos
existing_models = [model_name for model_name in model_names.keys() if os.path.isfile(os.path.join(model_folder, model_names[model_name]["model_path"]))]

def multiple_replace(text, replacements):
    # Iterar sobre cada par de remplazo
    for old, new in replacements:
        text = text.replace(old, new)
    return text

def filter_text(text, model_name):
    if model_name in model_names:
        replacements = model_names[model_name]["replacements"]
        # Realizar reemplazos específicos del modelo
        filtered_text = multiple_replace(text, replacements)
        # Escapar todos los caracteres especiales dentro de las comillas
        filtered_text = re.sub(r'(["\'])', lambda m: "\\" + m.group(0), filtered_text)
        return filtered_text
    else:
        logging.error(f"No se encontró el modelo '{model_name}'.")
        return None

def convert_text_to_speech(text, model_name):
    filtered_text = filter_text(text, model_name)[:3000]  # Limitar el texto a 3000 caracteres
    if filtered_text is None:
        return None

    random_name = ''.join(random.choices(string.ascii_letters + string.digits, k=8)) + '.wav'
    output_file = os.path.join(temp_audio_folder, random_name)

    if os.path.isfile(piper_binary_path) and model_name in model_names:
        model_path = os.path.join(model_folder, model_names[model_name]["model_path"])
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
            logging.error(f"Modelo '{model_name}' no encontrado en la ubicación especificada.")
            return None
    else:
        logging.error(f"No se encontró el binario de Piper en la ubicación especificada.")
        return None

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
    model_options = existing_models
    # Registra el contenido de la carpeta actual
    logging.info("Contents of current folder: %s", os.listdir(file_folder))
    return render_template('index.html', model_options=model_options)

@app.route('/convert', methods=['POST'])
@restrict_access
@rate_limit(1)  # Limita las solicitudes a 1 por segundo
def convert_text():
    text = request.form['text']
    model_name = request.form['model']
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

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'templates'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/image.jpg')
def image():
    return send_from_directory(os.path.join(app.root_path, 'templates'), 'image.jpg', mimetype='image/jpeg')

if __name__ == '__main__':
    logging.info("Se está iniciando la aplicación.")
    app.run(host='0.0.0.0', port=7860, debug=False)
