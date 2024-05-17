## Introduction

Welcome to the documentation of the speech synthesis application using Piper for Windows. This application allows converting text to speech in various languages and accents using custom and public speech synthesis models, which must be based on the .onnx format compatible with Piper. Additionally, it utilizes the Flask framework to create an interactive web interface.

![Screenshot](preview.png)

## Deploying the Application

To deploy the application, follow these steps:

1. Clone the repository to your server:

   ```bash
   git clone -b Windows https://github.com/HirCoir/HirCoir-Piper-tts-app.git
   ```

2. Enter the cloned repository directory:

   ```bash
   cd HirCoir-Piper-tts-app
   ```

3. Download Piper for Windows from the following link: [Piper Releases](https://github.com/rhasspy/piper/releases/)
   
4. Extract the `piper` folder from the downloaded file and place it in the project directory.

5. Run the `app.py` file with Python:

   ```bash
   python app.py
   ```

6. Select folder with models:
   Upon running `python app.py`, it will automatically open a window where you need to select the folder containing your .onnx models.

## Important Considerations

- Make sure you have Python installed on your system before running the application.
- You must have the .onnx voice models in a folder to be able to load them from `app.py`.

## Contributing

If you have suggestions to improve the application, consider opening an issue or making a pull request on the repository. This will help us enhance the application and provide a better user experience.

## Credits

Thanks to the developer of the original application and the creators of the speech synthesis models. Without their dedication and effort, this application would not be possible.

## License

The application is open source and distributed under the MIT License. Refer to the license for more details.
```
