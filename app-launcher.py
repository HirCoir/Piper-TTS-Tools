import logging
import os
import random
import re
import string
import subprocess
from tkinter import filedialog
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton, QHBoxLayout, QFileDialog, QComboBox, QMessageBox, QSlider
from PyQt5.QtCore import Qt, QUrl, QThread, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

# Configuración del registro
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define el directorio donde se guardan los archivos
file_folder = os.path.dirname(os.path.abspath(__file__))  # Obtiene la ruta del directorio actual del archivo
temp_audio_folder = os.path.join(file_folder, 'temp_audio')
model_folder = None
piper_binary_path = None  # Cambia la ruta al ejecutable de piper.exe en Windows

# Variable para omitir la selección de carpeta de modelos
use_models_folder = False  # Cambia a False para seleccionar la carpeta de modelos manualmente

if use_models_folder:
    model_folder = os.path.join(file_folder, 'models')

# Crea la carpeta temp_audio si no existe
os.makedirs(temp_audio_folder, exist_ok=True)

# Ajuste global para los reemplazos en el texto
global_replacements = [('\n', ' . '), ('*', ''), (')', '.'), ('#', '')]

def multiple_replace(text, replacements):
    # Iterar sobre cada par de remplazo
    for old, new in replacements:
        text = text.replace(old, new)
    return text

def filter_text(text):
    # Realizar reemplazos globales en el texto
    filtered_text = multiple_replace(text, global_replacements)
    # Escapar todos los caracteres especiales dentro de las comillas
    filtered_text = re.sub(r'(["\'])', lambda m: "\\" + m.group(0), filtered_text)
    return filtered_text

class ConvertTextToSpeechThread(QThread):
    conversion_done = pyqtSignal(str)

    def __init__(self, text, model_path, output_file):
        super().__init__()
        self.text = text
        self.model_path = model_path
        self.output_file = output_file

    def run(self):
        command = f'echo "{self.text}" | "{piper_binary_path}" -m "{self.model_path}" -f "{self.output_file}"'
        try:
            subprocess.run(command, shell=True, check=True)
            self.conversion_done.emit(self.output_file)
        except subprocess.CalledProcessError as e:
            logging.error(f"Error al ejecutar el comando: {e}")
            self.conversion_done.emit(None)

class TTSApp(QWidget):
    def __init__(self):
        super().__init__()
        self.player = QMediaPlayer()
        self.audio_file = None
        self.conversion_thread = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('ONNX - Convertidor de texto a voz')
        self.setGeometry(100, 100, 800, 600)  # Aumentado el tamaño de la ventana
        layout = QVBoxLayout()

        title = QLabel('Convertidor de Texto a Audio')
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet('font-size: 30px; font-weight: bold; color: white;')  # Aumentado el tamaño del texto
        layout.addWidget(title)

        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText('Introduce el texto aquí')
        self.text_input.setStyleSheet('background-color: #2E2E2E; color: white; font-size: 18px;')  # Aumentado el tamaño del texto
        layout.addWidget(self.text_input, 1)

        self.select_piper_button = QPushButton('Seleccionar carpeta de Piper')
        self.select_piper_button.setStyleSheet('background-color: #4CAF50; color: white; font-size: 18px;')  # Aumentado el tamaño del texto
        self.select_piper_button.clicked.connect(self.select_piper_folder)
        layout.addWidget(self.select_piper_button)

        self.model_spinner = QComboBox()
        self.model_spinner.setStyleSheet('background-color: #2E2E2E; color: white; font-size: 18px;')  # Aumentado el tamaño del texto
        if use_models_folder and model_folder:
            self.model_spinner.addItems([model for model in os.listdir(model_folder) if model.endswith('.onnx')])
        else:
            self.select_model_button = QPushButton('Seleccionar carpeta de modelos')
            self.select_model_button.setStyleSheet('background-color: #4CAF50; color: white; font-size: 18px;')  # Aumentado el tamaño del texto
            self.select_model_button.clicked.connect(self.select_model_folder)
            layout.addWidget(self.select_model_button)

        if use_models_folder:
            layout.addWidget(self.model_spinner)

        button_layout = QHBoxLayout()

        self.convert_button = QPushButton('Generar audio')
        self.convert_button.setStyleSheet('background-color: #4CAF50; color: white; font-size: 18px;')  # Aumentado el tamaño del texto
        self.convert_button.clicked.connect(self.convert_text)
        button_layout.addWidget(self.convert_button)

        self.save_button = QPushButton('Guardar audio')
        self.save_button.setStyleSheet('background-color: #4CAF50; color: white; font-size: 18px;')  # Aumentado el tamaño del texto
        self.save_button.clicked.connect(self.save_audio)
        button_layout.addWidget(self.save_button)

        layout.addLayout(button_layout)

        self.audio_label = QLabel('Aquí se reproducirá el audio')
        self.audio_label.setStyleSheet('color: white; font-size: 18px;')  # Aumentado el tamaño del texto
        layout.addWidget(self.audio_label)

        self.audio_controls = QHBoxLayout()
        self.play_button = QPushButton('Reproducir')
        self.play_button.setStyleSheet('background-color: #4CAF50; color: white; font-size: 18px;')  # Aumentado el tamaño del texto
        self.play_button.clicked.connect(self.play_audio)
        self.audio_controls.addWidget(self.play_button)

        self.pause_button = QPushButton('Pausar')
        self.pause_button.setStyleSheet('background-color: #4CAF50; color: white; font-size: 18px;')  # Aumentado el tamaño del texto
        self.pause_button.clicked.connect(self.pause_audio)
        self.audio_controls.addWidget(self.pause_button)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.sliderMoved.connect(self.set_position)
        self.slider.sliderPressed.connect(self.pause_audio)
        self.slider.sliderReleased.connect(self.play_audio)
        self.audio_controls.addWidget(self.slider)

        layout.addLayout(self.audio_controls)

        self.powered_by = QLabel('<a href="https://youtube.com/@hircoir" style="color: #4CAF50; font-size: 18px;">Powered by Hircoir</a>')  # Aumentado el tamaño del texto
        self.powered_by.setOpenExternalLinks(True)
        layout.addWidget(self.powered_by)

        self.setLayout(layout)

        self.player.positionChanged.connect(self.update_position)
        self.player.durationChanged.connect(self.update_duration)

    def select_piper_folder(self):
        selected_folder = QFileDialog.getExistingDirectory(self, 'Seleccionar carpeta de Piper')
        if selected_folder:
            piper_path = os.path.join(selected_folder, 'piper.exe')
            if os.path.isfile(piper_path):
                global piper_binary_path
                piper_binary_path = piper_path
                self.audio_label.setText(f'Piper seleccionado: {piper_path}')
            else:
                QMessageBox.warning(self, 'Error', 'No se encontró piper.exe en la carpeta seleccionada')
                self.style_error_message_box()

    def select_model_folder(self):
        selected_folder = QFileDialog.getExistingDirectory(self, 'Seleccionar carpeta de modelos')
        if selected_folder:
            model_files = [f for f in os.listdir(selected_folder) if f.endswith('.onnx')]
            if model_files:
                global model_folder
                model_folder = selected_folder
                self.model_spinner.addItems(model_files)
                if not use_models_folder:
                    self.layout().removeWidget(self.select_model_button)
                    self.select_model_button.deleteLater()
                    self.layout().insertWidget(3, self.model_spinner)
            else:
                QMessageBox.warning(self, 'Error', 'No se encontraron modelos en la carpeta seleccionada')
                self.style_error_message_box()

    def style_error_message_box(self):
        error_message = self.findChild(QMessageBox)
        if error_message:
            error_message.setStyleSheet("QLabel{color: white;} QPushButton{background-color: #4CAF50; color: white; font-size: 18px;}")  # Aumentado el tamaño del texto

    def convert_text(self):
        if piper_binary_path is None:
            QMessageBox.warning(self, 'Error', 'Por favor, selecciona la carpeta que contiene piper.exe')
            self.style_error_message_box()
            return

        text = self.text_input.toPlainText()
        model_name = self.model_spinner.currentText()
        filtered_text = filter_text(text)[:3000]  # Limitar el texto a 3000 caracteres
        if filtered_text is None:
            return

        random_name = ''.join(random.choices(string.ascii_letters + string.digits, k=8)) + '.wav'
        output_file = os.path.join(temp_audio_folder, random_name)

        if os.path.isfile(piper_binary_path) and model_folder is not None:
            model_path = os.path.join(model_folder, model_name)
            if os.path.isfile(model_path):
                self.audio_label.setText('Generando audio...')
                self.conversion_thread = ConvertTextToSpeechThread(filtered_text, model_path, output_file)
                self.conversion_thread.conversion_done.connect(self.on_conversion_done)
                self.conversion_thread.start()
            else:
                logging.error(f"Modelo '{model_name}' no encontrado en la ubicación especificada.")
        else:
            logging.error(f"No se encontró el binario de Piper en la ubicación especificada o no se ha seleccionado una carpeta de modelos.")

    def on_conversion_done(self, output_file):
        if output_file:
            self.audio_file = output_file
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile(self.audio_file)))
            self.audio_label.setText('Audio generado y listo para reproducir')
            self.play_audio()
        else:
            self.audio_label.setText('Error al convertir texto a voz')

    def play_audio(self):
        if self.audio_file:
            self.player.play()
            self.audio_label.setText('Reproducción en curso')

    def pause_audio(self):
        self.player.pause()
        self.audio_label.setText('Reproducción pausada')

    def set_position(self, position):
        self.player.setPosition(position)

    def update_position(self, position):
        self.slider.setValue(position)

    def update_duration(self, duration):
        self.slider.setRange(0, duration)

    def save_audio(self):
        if self.audio_file:
            file_path, _ = QFileDialog.getSaveFileName(self, 'Guardar audio', '', 'Audio Files (*.wav)')
            if file_path:
                try:
                    os.rename(self.audio_file, file_path)
                    self.audio_label.setText(f'Audio guardado: {file_path}')
                except Exception as e:
                    logging.error(f"Error al guardar el archivo: {e}")
                    self.audio_label.setText('Error al guardar el audio')
            else:
                self.audio_label.setText('Guardado cancelado')

if __name__ == '__main__':
    app = QApplication([])
    app.setStyleSheet('''
        QWidget {
            background-color: #222;
            color: #fff;
            font-family: Arial, sans-serif;
        }
        QComboBox, QTextEdit, QPushButton {
            background-color: #2E2E2E;
            color: white;
            border: 1px solid #4CAF50;
            border-radius: 5px;
            padding: 10px;  # Aumentado el tamaño del texto
        }
        QPushButton:hover {
            background-color: #4CAF50;
        }
    ''')
    icon_path = os.path.join(file_folder, 'icon.ico')
    app.setWindowIcon(QIcon(icon_path))
    window = TTSApp()
    window.show()
    app.exec_()
