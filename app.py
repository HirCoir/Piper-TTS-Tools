import logging
import os
import random
import re
import string
import subprocess
import time
import base64
import sqlite3
from flask import Flask, render_template, request, jsonify, after_this_request, send_from_directory
from functools import wraps
from datetime import datetime, timedelta

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
    "Español España | Nate Gentile": {
        "model_path": "es_MX-Nate.onnx",
        "replacements": [('\n', ' . '), ('*', ''), (')', ',')]
    },
    "Español México | Lucasmelor": {
        "model_path": "es_MX_Lucasmelor-high.onnx",
        "replacements": [('\n', ' . '), ('*', ''), (')', ',')]
    },
    "Español México | DocTops": {
        "model_path": "es_MX-DocTops.onnx",
        "replacements": [('\n', ' . '), ('*', ''), (')', ',')]
    },
    "Español México | Sorah Neuronal": {
        "model_path": "es_MX-sorah-high.onnx",
        "replacements": [('\n', ' . '), ('*', ''), (')', ',')]
    },
    "Español México | Laura Neuronal": {
        "model_path": "es_MX-laura-high.onnx",
        "replacements": [('\n', ' . '), ('*', ''), (')', ',')]
    },
    "Español México | Emma Neuronal": {
        "model_path": "es_MX-emma-high.onnx",
        "replacements": [('\n', ' . '), ('*', ''), (')', ',')]
    },
    "Español México | Kamora Neuronal": {
        "model_path": "kamora.onnx",
        "replacements": [('\n', ''), ('*', ''), (')', ',')]
    },
    "Español México | Voz HirCoir": {
        "model_path": "es_MX-HirCoir.onnx",
        "replacements": [('(', ','), (')', ','), ('?', ','), ('¿', ','), (':', ','), ('\n', ' '), (')', ',')]
    },
    "Español México    | Claude": {
        "model_path": "es_MX-claude-14947-epoch-high.onnx",
        "replacements": [('(', ','), (')', ','), ('?', ','), ('¿', ','), (':', ','), ('\n', ' '), (')', ',')]
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
    for old, new in replacements:
        text = text.replace(old, new)
    return text

def filter_text(text, model_name):
    if model_name in model_names:
        replacements = model_names[model_name]["replacements"]
        filtered_text = multiple_replace(text, replacements)
        filtered_text = re.sub(r'(["\'])', lambda m: "\\" + m.group(0), filtered_text)
        return filtered_text
    else:
        logging.error(f"No se encontró el modelo '{model_name}'.")
        return None

def convert_text_to_speech(text, model_name):
    filtered_text = filter_text(text, model_name)[:1000]
    if filtered_text is None:
        return None

    random_name = ''.join(random.choices(string.ascii_letters + string.digits, k=8)) + '.wav'
    output_file = os.path.join(temp_audio_folder, random_name)

    if os.path.isfile(piper_binary_path) and model_name in model_names:
        model_path = os.path.join(model_folder, model_names[model_name]["model_path"])
        if os.path.isfile(model_path):
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

# Configuración de la base de datos SQLite
db_path = 'rate_limit.db'

def init_db():
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS requests (
                            ip TEXT,
                            timestamp DATETIME
                          )''')
        conn.commit()

init_db()

def rate_limit(limit, period):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            ip = request.remote_addr
            now = datetime.now()
            window_start = now - timedelta(seconds=period)

            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM requests WHERE timestamp < ?", (window_start,))
                cursor.execute("SELECT COUNT(*) FROM requests WHERE ip = ? AND timestamp >= ?", (ip, window_start))
                request_count = cursor.fetchone()[0]

                if request_count >= limit:
                    return jsonify({'error': 'Too many requests. Please try again later.'}), 429

                cursor.execute("INSERT INTO requests (ip, timestamp) VALUES (?, ?)", (ip, now))
                conn.commit()

            return func(*args, **kwargs)
        return wrapper
    return decorator

def restrict_access(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        referer = request.headers.get("Referer")
        if referer and referer.endswith("/"):
            return func(*args, **kwargs)
        else:
            return "Acceso no autorizado", 403
    return wrapper

@app.route('/')
def index():
    domain_url = request.url_root
    model_options = existing_models
    logging.info("Contents of current folder: %s", os.listdir(file_folder))
    return render_template('index.html', model_options=model_options, domain_url=domain_url)


@app.route('/og-image.jpg')
def og_image():
    return send_from_directory(os.path.join(app.root_path, 'templates'), 'og-image.jpg', mimetype='image/jpg')

@app.route('/convert', methods=['POST'])
@restrict_access
@rate_limit(5, 60)  # Limita las solicitudes a 5 por minuto por IP
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
