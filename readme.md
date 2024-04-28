# Piper TTS Flask API

This Flask API allows you to convert text to speech using the [PIPER](https://github.com/rhasspy/piper) text-to-speech engine. Piper is a fast, local neural text-to-speech system optimized for Raspberry Pi 4. The API supports multiple languages, and the voices are trained with VITS and then exported to onnxruntime.

Each voice requires two files:

- A .onnx model file (e.g., en_US-lessac-medium.onnx)
- An .onnx.json configuration file (e.g., en_US-lessac-medium.onnx.json)

The API supports multiple languages, and the voices are trained with VITS and then exported to onnxruntime. The Piper TTS API allows you to choose different voices from the [community-created voices](https://huggingface.co/rhasspy/piper-voices/tree/main) on the HuggingFace repository.

The application uses community-created voices from Rhasspy's HuggingFace repository, the creator of Piper. Models can be easily added and listed using the format in the app.py file.

```python
"kamora": {
    "model_path": "es_MX-kamora-tiny-x-low.onnx",
    "replacements": [('\n', '. '), ('*', '')]
}
```
Where "kamora" is the name displayed to the user when accessing /models.
The "model_path" "es_MX-kamora-tiny-x-low.onnx" is the specific file name of your model in the models folder. The "replacements" field within the model dictionary is for replacing specific elements in the text before sending it to the model in case your model does not handle certain characters like periods, exclamation marks, and others, which should be replaced with a comma to introduce a pause.

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

NOTE: The mentioned replacements (`('\n', '. '),('*', '')`) should always be added and are necessary for the functionality of Piper's binary.

The MODEL_CARD file contains important license information. Please review it carefully, as some voices may have restrictive licenses.

### Setting a Secret Key in Linux to Access the API

To protect your API and allow only requests with a valid token to access it, you can set up a secret key in your Linux system and then use it in your code. Here is how to do it step by step:

#### Configure the Secret Key

1. **Set a secret key** that only you will know. This key can be set in an environment variable called `SECRET_KEY` in your Linux system.

2. **Define the environment variable**:

   You can define the `SECRET_KEY` variable in various ways in your system:

   - **Temporarily in a terminal session**:

     In the terminal, you can set the variable using the following command:
     ```shell
     export SECRET_KEY="your_secret_key"
     ```

     The variable will only be available in the current terminal session. Once you close the session, the variable will no longer be available.

   - **Permanently**:

     To make the variable persistent across sessions, you need to add it to an environment configuration file. For example, in **`~/.bashrc`** or **`~/.profile`**.

     Open one of these files in a text editor, for example, `nano`:
     ```shell
     nano ~/.bashrc
     ```

     Add the following line at the end of the file:
     ```shell
     export SECRET_KEY="your_secret_key"
     ```

     Save and close the file. Then, refresh your terminal configuration:
     ```shell
     source ~/.bashrc
     ```

3. **Verify that the environment variable is set**:

   You can verify that the `SECRET_KEY` variable is set correctly with the following command:
   ```shell
   echo $SECRET_KEY
   ```

   This command should display the secret key you configured.

## API Usage Examples

The API supports multiple programming languages:

### Node.js

```node
const axios = require('axios');
const fs = require('fs');

const url = 'http://127.0.0.1:7860/convert';

// Authentication token (replace 'your_secret_token' with your secret key)
const token = 'your_secret_token';

const data = {
    text: "This is an example text\nwith multiple line breaks\nto test the functionality\nof the client code.",
    model: "kamora"
};

axios.post(url, data, {
    headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    }
})
.then(response => {
    const audioBase64 = response.data.audio_base64;
    const audioBytes = Buffer.from(audioBase64, 'base64');

    // Save the audio file
    fs.writeFileSync('output.wav', audioBytes);
    console.log('Audio saved as output.wav');
})
.catch(error => {
    console.error('Error obtaining audio:', error.response.status);
});
```

### Python

```python
import requests
import base64
import json

# API URL
url = 'http://127.0.0.1:7860/convert'

# Authentication token (replace 'your_secret_token' with your secret key)
token = 'your_secret_token'

# Add the token to the request headers
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {token}'
}

# Text data with line breaks and model to use
data = {
    "text": "This is an example text\nwith multiple line breaks\nto test the functionality\nof the client code.",
    "model": "kamora"
}

# Convert the data to JSON
data_json = json.dumps(data)

# Send the POST request to the Flask server
response = requests.post(url, headers=headers, data=data_json)

# Handle the response
if response.status_code == 200:
    response_data = response.json()
    audio_base64 = response_data['audio_base64']
    audio_bytes = base64.b64decode(audio_base64)

    # Save the audio file
    with open('output.wav', 'wb') as f:
        f.write(audio_bytes)
    print('Audio saved as output.wav')
else:
    print('Error obtaining audio:', response.status_code)
```

### Curl

```bash
curl -X POST \
  http://127.0.0.1:7860/convert \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer your_secret_token' \
  -d '{
    "text": "This is an example text\nwith multiple line breaks\nto test the functionality\nof the client code.",
    "model": "kamora"
  }'
```

## Building the Docker Image

The Docker image for this project can be built using the provided Dockerfile. The Dockerfile defines a base image, installs the required packages, and sets up the environment for the application.

The Dockerfile includes instructions for handling environment variables, which can be used to download your personal models if you have any.

- `TOKEN_HUGGINGFACE` should be used to set the Hugging Face token. This token is stored in `.cache/huggingface/token` for future use if not NULL.

- `REPO_HUGGINGFACE` should be defined to specify the Hugging Face repository, to download specific models. These models are typically stored in the `models` directory.
```bash
# Build the Docker image
docker build --build-arg TOKEN_HUGGINGFACE=<your-token> --build-arg REPO_HUGGINGFACE=<your-repo> -t piper-tts-app .

# Run the Docker image
docker run -p 7860:7860 piper-tts-app
```
Replace `<your-token>` and `<your-repo>` with your Hugging Face token and repository respectively.

Remember to review the license information for the voice models you are using.

Happy Text-to-Speech Conversion!
