# Piper TTS Flask API

This Flask API enables you to convert text to speech using the [PIPER](https://github.com/rhasspy/piper) text-to-speech engine. Piper is a fast and local neural text-to-speech system optimized for Raspberry Pi 4. The API supports multiple languages, and the voices are trained with VITS and then exported to onnxruntime.

Each voice requires two files:

- A .onnx model file (e.g., en_US-lessac-medium.onnx)
- A .onnx.json config file (e.g., en_US-lessac-medium.onnx.json)

The API supports several languages, and the voices are trained with VITS and then exported to onnxruntime. The Piper TTS API allows you to choose different voices from the [community-created voices](https://huggingface.co/rhasspy/piper-voices/tree/main) in the HuggingFace repository.

The MODEL_CARD file contains important licensing information. Please review it carefully as some voices may have restrictive licenses.

## API Usage Examples

The API supports multiple programming languages:

### Node.js

```node
const axios = require('axios');

const url = 'http://127.0.0.1:7860/convert';
const data = {
    text: "This is an example text\nwith multiple line breaks\nto test the functionality\nof the client code.",
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
    console.log('Audio saved as output.wav');
})
.catch(error => {
    console.error('Error obtaining the audio:', error.response.status);
});
```

### Python

```python
import requests
import base64
import json

url = 'http://127.0.0.1:7860/convert'
headers = {'Content-Type': 'application/json'}

# Text with line breaks
data = {
    "text": "This is an example text\nwith multiple line breaks\nto test the functionality\nof the client code.",
    "model": "kamora"
}

# Convert to JSON
data_json = json.dumps(data)

# Send request to the Flask server
response = requests.post(url, headers=headers, data=data_json)

# Handle the response
if response.status_code == 200:
    response_data = response.json()
    audio_base64 = response_data['audio_base64']
    audio_bytes = base64.b64decode(audio_base64)

    with open('output.wav', 'wb') as f:
        f.write(audio_bytes)
    print('Audio saved as output.wav')
else:
    print('Error obtaining the audio:', response.status_code)
```

### Curl

```bash
curl -X POST \
  http://127.0.0.1:7860/convert \
  -H 'Content-Type: application/json' \
  -d '{
    "text": "This is an example text\nwith multiple line breaks\nto test the functionality\nof the client code.",
    "model": "kamora"
  }'
```

Help/documentation is available from the server using [http://127.0.0.1:8080/help](http://127.0.0.1:8080/help).
