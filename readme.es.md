# Piper TTS Flask API

Esta API de Flask te permite convertir texto a voz utilizando el motor de texto a voz [PIPER](https://github.com/rhasspy/piper). Piper es un sistema rápido y local de texto a voz neuronal optimizado para Raspberry Pi 4. La API admite varios idiomas, y las voces están entrenadas con VITS y luego exportadas a onnxruntime.


Cada voz requiere dos archivos:

- Un archivo de modelo .onnx (por ejemplo, en_US-lessac-medium.onnx)
- Un archivo de configuración .onnx.json (por ejemplo, en_US-lessac-medium.onnx.json)

La API admite varios idiomas, y las voces están entrenadas con VITS y luego exportadas a onnxruntime. La API de Piper TTS permite elegir diferentes voces de los [voces creadas por la comunidad](https://huggingface.co/rhasspy/piper-voices/tree/main) en el repositorio de HuggingFace.

La aplicación utiliza las voces creadas por la comunidad del repositorio de HuggingFace de Rhasspy, el creador de Piper. Los modelos pueden ser fácilmente añadidos y listados utilizando el formato en el archivo app.py

```python
"kamora": {
        "model_path": "es_MX-kamora-tiny-x-low.onnx",
        "replacements": [('\n', '. '),('*', '')]
    }
```
donde "Kamora" es el nombre mostrado al usuario al acceder a /models. 
La "model_path" "es_MX-kamora-tiny-x-low.onnx" es el nombre de archivo específico de tu modelo en la carpeta de modelos. El campo "replacements" dentro del diccionario de modelo es para reemplazar elementos específicos en el texto antes de enviarlo al modelo en caso de que tu modelo no omita ciertos caracteres como puntos, signos de exclamación y otros para ser reemplazados por una coma para dar una pausa.

Lo siguiente es un ejemplo del campo "replacements":

```python
"replacements": [('(', ','), (')', ','), ('?', ','), ('¿', ','), (':', ','), ('\n', ' ')]
```
Esto reemplaza lo siguiente:

- `(` con `,`
- `)` con `,`
- `?` con `,`
- `¿` con `,`
- `:` con `,`
- `\n` con ` ` 

NOTA: Los reemplazos mencionados (`('\n', '. '),('*', '')`) siempre deben ser agregados y son necesarios para la funcionalidad del binario de Piper.

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

## Construyendo la Imagen de Docker

La imagen de Docker para este proyecto se puede construir utilizando el Dockerfile proporcionado. El Dockerfile define una imagen base, instala los paquetes requeridos y configura el entorno para la aplicación.

El Dockerfile incluye instrucciones para gestionar variables de entorno, las cuales pueden ser utilizadas para descargar tus modelos personales si tienes alguno. 

- `TOKEN_HUGGINGFACE` debe ser utilizado para establecer el token de Hugging Face. Este token se guarda en `.cache/huggingface/token` para usos futuros si no es NULL.

- `REPO_HUGGINGFACE` debe ser definido para especificar el repositorio de Hugging Face, para descargar los modelos específicos. Estos modelos típicamente se guardan en el directorio `models`.
```bash
# Construir la imagen de Docker
docker build --build-arg TOKEN_HUGGINGFACE=<tu-token> --build-arg REPO_HUGGINGFACE=<tu-repo> -t piper-tts-app .

# Ejecutar la imagen de Docker
docker run -p 7860:7860 piper-tts-app
```
Reemplaza `<tu-token>` y `<tu-repo>` con tu token y repositorio de Hugging Face respectivamente.

Recuerda revisar la información de licencia de los modelos de voz que estás utilizando.

¡Feliz Conversión de Texto a Voz!
