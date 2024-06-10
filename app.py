import os
import random
import re
import string
import subprocess
import base64
import logging
import shlex
from flask import Flask, request, jsonify

app = Flask(__name__)

temp_audio_folder = "/home/app/temp_audio"
piper_binary_path = "/home/app/piper/piper"
model_folder = "/home/app/models/"

# Define los nombres asignados a modelos específicos
model_names = {
    "sorah": {
        "model_path": "es_MX-sorah-high.onnx",
        "replacements": [('\n', '. '),('*', '')]
    },
    "nate": {
        "model_path": "es_MX-Nate.onnx",
        "replacements": [('\n', '. '),('*', '')]
    },
    "emma": {
        "model_path": "es_MX-emma-high.onnx",
        "replacements": [('\n', '. '),('*', '')]
    },
    "hircoir": {
        "model_path": "es_MX-hircoir-22479-high.onnx",
        "replacements": [('\n', '. '),('*', '')]
    },
    "laura": {
        "model_path": "es_MX-laura-high.onnx",
        "replacements": [('\n', '. '),('*', ''),(')', '')]
    },
    "kamora": {
        "model_path": "kamora.onnx",
        "replacements": [('\n', '. '),('*', '')]
    }
    ,
    "Angel": {
        "model_path": "es_MX-modelo1-high.onnx",
        "replacements": [('\n', '. '),('*', '')]
    }
}
# Variable para almacenar el token secreto
secret_key = os.environ.get('SECRET_KEY', 'default_secret_key')

# Verifica si los modelos definidos existen en la carpeta de modelos
existing_models = [model_name for model_name in model_names.keys() if os.path.isfile(os.path.join(model_folder, model_names[model_name]["model_path"]))]

def multiple_replace(text, replacements):
    # Iterar sobre cada par de remplazo
    for old, new in replacements:
        text = text.replace(old, new)
    return text

def remove_emojis(text):
    # Definir un patrón regex para los emojis
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002702-\U000027B0"  # Dingbats
        "\U000024C2-\U0001F251" 
        "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

def filter_text(text, model_name, remove_emojis_flag=False):
    if model_name in model_names:
        replacements = model_names[model_name]["replacements"]
        # Realizar reemplazos específicos del modelo
        filtered_text = multiple_replace(text, replacements)
        if remove_emojis_flag:
            filtered_text = remove_emojis(filtered_text)
        # Eliminar caracteres especiales usando shlex
        filtered_text = shlex.quote(filtered_text)
        return filtered_text
    else:
        logging.error(f"No se encontró el modelo '{model_name}'.")
        return None

# Define una función para convertir texto a voz
def convert_text_to_speech(text, model_name, remove_emojis_flag=True):
    filtered_text = filter_text(text, model_name, remove_emojis_flag)[:50000]
    if filtered_text is None:
        return None

    random_name = ''.join(random.choices(string.ascii_letters + string.digits, k=8)) + '.wav'
    output_file = os.path.join(temp_audio_folder, random_name)

    if os.path.isfile(piper_binary_path):
        model_path = os.path.join(model_folder, model_names[model_name]["model_path"])
        if os.path.isfile(model_path):
            command = f'echo {filtered_text} | "{piper_binary_path}" -m {model_path} -f {output_file}'
            print(f"Executing: {command}")
            try:
                subprocess.run(command, shell=True, check=True)
                with open(output_file, "rb") as f:
                    audio_data = f.read()
                audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                return audio_base64
            except subprocess.CalledProcessError as e:
                print(f"Error ejecutando el comando: {e}")
                return None
        else:
            print(f"Modelo '{model_name}' no encontrado.")
            return None
    else:
        print(f"Piper binary no encontrado.")
        return None

# Función para autenticar el token en las solicitudes
def authenticate_request():
    token = request.headers.get('Authorization')
    if not token or token != f'Bearer {secret_key}':
        return jsonify({"error": "Unauthorized"}), 401
    return None

@app.route('/convert', methods=['POST'])
def convert_text():
    auth_response = authenticate_request()
    if (auth_response):
        return auth_response

    data = request.get_json()
    if 'text' not in data or 'model' not in data:
        return jsonify({"error": "Missing 'text' or 'model' in request."}), 400

    text = data['text']
    model_name = data['model']
    remove_emojis_flag = data.get('remove_emojis', False)

    audio_base64 = convert_text_to_speech(text, model_name, remove_emojis_flag)
    if audio_base64:
        return jsonify({"audio_base64": audio_base64})
    else:
        return jsonify({"error": "Conversion failed."}), 500

@app.route('/models', methods=['GET'])
def list_models():
    auth_response = authenticate_request()
    if (auth_response):
        return auth_response

    model_options = list(model_names.keys())
    return jsonify(model_options)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860, debug=True)
