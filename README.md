 ## Introduction

Welcome to the documentation for the text-to-speech application using Piper. This application allows you to convert text to speech in various languages and accents using custom and public TTS models, these models must be based on the .onnx format compatible with Piper. Furthermore, it uses the Flask framework to create an interactive web interface and the Hugging Face library to download and use all TTS models.

## Deploying the App

To deploy the application, follow the steps below:

1. Clone the repository to your server:

```
git clone https://github.com/HirCoir/HirCoir-Piper-tts-app.git
```

2. Change to the cloned repository directory:

```
cd HirCoir-Piper-tts-app
```

3. Build the Docker container:

```
docker build --build-arg TOKEN_HUGGINGFACE=your-huggingface-token --build-arg REPO_HUGGINGFACE=your-huggingface-repo .
```

In this step, provide your Hugging Face token to download private voice models and the Hugging Face repository where your custom voice models are located. If you do not have custom models, simply ignore the `--build-arg TOKEN_HUGGINGFACE=your-huggingface-token --build-arg REPO_HUGGINGFACE=your-huggingface-repo` environment variable.

4. Run the container:

```
docker run -d --name tts-app -p 7860:7860 tts-app
```

This will run the application on port 7860 and allow you to access it in your web browser at `localhost:7860`.

## Important Considerations

- Make sure Docker and Git are installed on your server before running these commands.
- Do not share your Hugging Face token with anyone. It is sensitive and if misused, could cause problems with your Hugging Face account.
- Hugging Face TTS models can be heavy and take time to download. Please be patient.

## Contribute

If you have suggestions to improve the application, consider opening an issue or making a pull request in the repository. This will help me improve the application and provide a better user experience.

## Credits

Thank you to the original application developer and the creators of the TTS models. Without their dedication and effort, this application would not be possible.

## License

The application is open source and is distributed under the MIT license. See the license for more details.
