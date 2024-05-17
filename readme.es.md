# Piper TTS Flask API

Esta API de Flask te permite convertir texto a voz utilizando el motor de texto a voz [PIPER](https://github.com/rhasspy/piper). Piper es un sistema rápido y local de texto a voz neuronal optimizado para Raspberry Pi 4. La API admite varios idiomas, y las voces están entrenadas con VITS y luego exportadas a onnxruntime.


Cada voz requiere dos archivos:

- Un archivo de modelo .onnx (por ejemplo, en_US-lessac-medium.onnx)
- Un archivo de configuración .onnx.json (por ejemplo, en_US-lessac-medium.onnx.json)

La API admite varios idiomas, y las voces están entrenadas con VITS y luego exportadas a onnxruntime. La API de Piper TTS permite elegir diferentes voces de los [voces creadas por la comunidad](https://huggingface.co/rhasspy/piper-voices/tree/main) en el repositorio de HuggingFace.

El archivo MODEL_CARD contiene información de licencia importante. Por favor, revísalo cuidadosamente ya que algunas voces pueden tener licencias restrictivas.

## Ejemplos de Uso de la API

La API admite varios lenguajes de programación:

### Node.js 

```node
const axios = require('axios');

const url = 'http://127.0.0.1:7860/convert';
const data = {
    text: "Este es un ejemplo de texto\ncon múltiples saltos de línea\npara probar la funcionalidad\ndel código del cliente.",
    model: "kamora"
};

axios.post(url, data, {
    headers: {
        'Content-Type': 'application/json'
    }
})
.then(response => {
    const audioBase64 = response.data.audio_base64;
    const audioBytes = Buffer.from(audioBase64, 'base64');

    require('fs').writeFileSync('output.wav', audioBytes);
    console.log('Audio guardado como output.wav');
})
.catch(error => {
    console.error('Error obteniendo el audio:', error.response.status);
});
```

### Python

```python
import requests
import base64
import json

url = 'http://127.0.0.1:7860/convert'
headers = {'Content-Type': 'application/json'}

# Texto con saltos de línea
data = {
    "text": "Este es un ejemplo de texto\ncon múltiples saltos de línea\npara probar la funcionalidad\ndel código del cliente.",
    "model": "kamora"
}

# Convertir a JSON
data_json = json.dumps(data)

# Enviar la solicitud al servidor de Flask
response = requests.post(url, headers=headers, data=data_json)

# Manejar la respuesta
if response.status_code == 200:
    response_data = response.json()
    audio_base64 = response_data['audio_base64']
    audio_bytes = base64.b64decode(audio_base64)

    with open('output.wav', 'wb') as f:
        f.write(audio_bytes)
    print('Audio guardado como output.wav')
else:
    print('Error obteniendo el audio:', response.status_code)
```

### Curl

```bash
curl -X POST \
  http://127.0.0.1:7860/convert \
  -H 'Content-Type: application/json' \
  -d '{
    "text": "Este es un ejemplo de texto\ncon múltiples saltos de línea\npara probar la funcionalidad\ndel código del cliente.",
    "model": "kamora"
  }'

```
