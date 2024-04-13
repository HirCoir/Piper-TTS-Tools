# Piper TTS Flask API

This Flask API allows you to convert text to speech using the [PIPER](https://github.com/rhasspy/piper) text to speech engine. Piper is a fast and local neural text to speech system optimized for Raspberry Pi 4. The API supports several languages, and the voices are trained with VITS and then exported to onnxruntime.


Each voice requires two files:

- A .onnx model file (e.g., en_US-lessac-medium.onnx)
- A .onnx.json config file (e.g., en_US-lessac-medium.onnx.json)

The API supports several languages, and the voices are trained with VITS and then exported to onnxruntime. The Piper TTS API allows to choose different voices from the [community-created voices](https://huggingface.co/rhasspy/piper-voices/tree/main) in the HuggingFace repository.

The application uses the community-created voices from the HuggingFace repository of rhasspy, the creator of Piper. Models can be easily added and listed using the format in the app.py

```python
"kamora": {
        "model_path": "es_MX-kamora-tiny-x-low.onnx",
        "replacements": [('\n', '. '),('*', '')]
    }
```
where "Kamora" is the name shown to the user when accessing /models. 
The model_path "es_MX-kamora-tiny-x-low.onnx" is the specific filename of your model in the models folder. The "replacements" field inside the model dictionary is to replace specific elements in the text before sending it to the model in case your model might not omit certain characters such as periods, exclamation marks, and others to be replaced by a comma to give a pause.

The following is an example of the "replacements" field:

```python
"replacements": [('(', ','), (')', ','), ('?', ','), ('¿', ','), (':', ','), ('\n', ' ')]
```
This replaces the following:

- `(` with `,`
- `)` with `,`
- `?` with `,`
- `¿` with `,`
- `:` with `,`
- `\n` with ` ` 

NOTE: The mentioned replacements (`('\n', '. '),('*', '')`) must always be added and they are necessary for the functionality of the Piper binary.

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

## Building the Docker Image

The Docker image for this project can be built using the Dockerfile provided. The Dockerfile defines a base image, installs the required packages, and sets up the environment for the application.

The Dockerfile includes instructions for managing environment variables, which can be used to download your personal models if you have any. 

- `TOKEN_HUGGINGFACE` should be used to set the Hugging Face token. This token is saved to the `.cache/huggingface/token` for future uses if not NULL.

- `REPO_HUGGINGFACE` should be defined to specify the Hugging Face repository, to download the specific models. These models are typically saved to the `models` directory.
```bash
# Build the Docker image
docker build --build-arg TOKEN_HUGGINGFACE=<your-token> --build-arg REPO_HUGGINGFACE=<your-repo> -t piper-tts-app .

# Run the Docker image
docker run -p 7860:7860 piper-tts-app
```
Replace `<your-token>` and `<your-repo>` with your actual Hugging Face token and repository respectively.

Remember to review the licensing information for the voice models you're using. 

Happy Text-to-Speech Converting!
