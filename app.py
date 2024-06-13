import os
import random
import re
import string
import subprocess
import base64
import logging
from flask import Flask, request, jsonify
import shlex

app = Flask(__name__)

temp_audio_folder = "/home/app/temp_audio"
piper_binary_path = "/home/app/piper/piper"
model_folder = "/home/app/models/"

# Define los nombres asignados a modelos específicos, en caso de no existir no se muestran
model_names = {
    "NateGentile": {
        "model_path": "es_MX-Nate.onnx",
        "replacements": [('\n', ' . '), ('*', ''), ('#', '')]
    },
    "Veritasium": {
        "model_path": "es_MX-Veritasium-high.onnx",
        "replacements": [('\n', ' . '), ('*', ''), ('#', '')]
    },
    "1PesoDeSalsa": {
        "model_path": "es_MX-1PesoDeSalsa-high.onnx",
        "replacements": [('\n', ' . '), ('*', ''), ('#', '')]
    },
    "Lucasmelor": {
        "model_path": "es_MX_Lucasmelor-high.onnx",
        "replacements": [('\n', ' . '), ('*', ''), ('#', '')]
    },
    "DocTops": {
        "model_path": "es_MX-DocTops.onnx",
        "replacements": [('\n', ' . '), ('*', ''), ('#', '')]
    },
    "Sorah": {
        "model_path": "es_MX-sorah-high.onnx",
        "replacements": [('\n', ' . '), ('*', ''), ('#', '')]
    },
    "Laura": {
        "model_path": "es_MX-laura-high.onnx",
        "replacements": [('\n', ' . '), ('*', ''), ('#', '')]
    },
    "Emma": {
        "model_path": "es_MX-emma-high.onnx",
        "replacements": [('\n', ' . '), ('*', ''), ('#', '')]
    },
    "Kamora": {
        "model_path": "kamora.onnx",
        "replacements": [('\n', ''), ('*', ''), ('#', '')]
    },
    "HirCoir": {
        "model_path": "es_MX-HirCoir.onnx",
        "replacements": [('(', ','), (')', ','), ('?', ','), ('¿', ','), (':', ','), ('\n', ' '), (')', ',')]
    },
    "Claude": {
        "model_path": "es_MX-claude-14947-epoch-high.onnx",
        "replacements": [('(', ','), (')', ','), ('?', ','), ('¿', ','), (':', ','), ('\n', ' '), (')', ',')]
    },
    "Angel": {
        "model_path": "es_MX-modelo1-high.onnx",
        "replacements": [('\n', '. '),('*', '')]
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
        # Eliminar caracteres especiales usando shlex
        filtered_text = shlex.quote(filtered_text)
        return filtered_text
    else:
        logging.error(f"No se encontró el modelo '{model_name}'.")
        return None

# Define una función para convertir texto a voz
def convert_text_to_speech(text, model_name):
    filtered_text = filter_text(text, model_name)[:50000]  # Limitar el texto a 500 caracteres
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
                print(f"Error executing command: {e}")
                return None
        else:
            print(f"Model '{model_name}' not found at the specified location.")
            return None
    else:
        print(f"Piper binary not found at the specified location.")
        return None

@app.route('/convert', methods=['POST'])
def convert_text():
    data = request.get_json()
    if 'text' not in data or 'model' not in data:
        return jsonify({"error": "Missing 'text' or 'model' in request."}), 400
    
    text = data['text']
    model_name = data['model']
    
    audio_base64 = convert_text_to_speech(text, model_name)
    if audio_base64:
        return jsonify({"audio_base64": audio_base64})
    else:
        return jsonify({"error": "Conversion failed."}), 500

@app.route('/models', methods=['GET'])
def list_models():
    model_options = list(model_names.keys())
    return jsonify(model_options)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860, debug=True)
