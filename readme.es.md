## Introducción

Bienvenido a la documentación de la aplicación de síntesis de voz utilizando Piper para Windows. Esta aplicación permite convertir texto a voz en varios idiomas y acentos utilizando modelos de síntesis de voz personalizados y públicos, dichos modelos deben de ser basados en el formato .onnx compatible con Piper. Además, utiliza el framework Flask para crear una interfaz web interactiva.

![Captura](preview.png)

## Despliegue de la Aplicación

Para desplegar la aplicación, sigue los siguientes pasos:

1. Clona el repositorio en tu servidor:

   ```bash
   git clone -b Windows https://github.com/HirCoir/HirCoir-Piper-tts-app.git
   ```

2. Entra al directorio del repositorio clonado:

   ```bash
   cd HirCoir-Piper-tts-app
   ```

3. Ejecuta el archivo `app.py` con Python:

   ```bash
   python app.py
   ```
   
4. Seleccionar carpeta con modelos:
   Al ejecutar `python app.py` este automáticamente abrirá una ventaja donde debe de seleccionar la carpeta de sus modelos .onnx.

## Consideraciones Importantes

- Asegúrate de tener Python instalado en tu sistema antes de ejecutar la aplicación.
- Debes de tener los modelos de voz .onnx en una carpeta para poder cargarlos desde la app.py

## Contribuir

Si tienes sugerencias para mejorar la aplicación, considera abrir un issue o hacer un pull request en el repositorio. Esto nos ayudará a mejorar la aplicación y proporcionar una mejor experiencia de usuario.

## Créditos

Gracias al desarrollador de la aplicación original y a los creadores de los modelos de síntesis de voz. Sin su dedicación y esfuerzo, esta aplicación no sería posible.

## Licencia

La aplicación es de código abierto y se distribuye bajo la licencia MIT. Consulta la licencia para más detalles.
