"""
Google Text-to-Speech GUI Application
Using PyQt6 and gTTS
"""

import sys
from pathlib import Path
from typing import Optional
import pygame

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QComboBox, QTextEdit, QPushButton, QFileDialog, QProgressBar,
    QLabel, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QIcon
from gtts import gTTS
import gtts.lang

class TTSWorker(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, text: str, lang: str, tld: str):
        super().__init__()
        self.text = text
        self.lang = lang
        self.tld = tld
        
    def run(self):
        try:
            temp_file = Path('temp.mp3')
            tts = gTTS(text=self.text, lang=self.lang, tld=self.tld)
            tts.save(str(temp_file))
            self.finished.emit(str(temp_file))
        except Exception as e:
            self.error.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Google Text-to-Speech')
        self.setMinimumSize(600, 400)
        
        # Initialize pygame mixer for audio playback
        pygame.mixer.init()
        
        # Timer for checking music end
        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self.check_music_end)
        self.check_timer.start(100)  # Check every 100ms
        
        # Audio state
        self.current_sound: Optional[str] = None
        self.is_playing = False
        
        # Create the central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Language selection
        lang_layout = QHBoxLayout()
        self.lang_combo = QComboBox()
        
        # Get languages with their full names
        languages = gtts.lang.tts_langs()
        # Modify Catalan to Catalan-Valencian
        if 'ca' in languages:
            languages['ca'] = 'Catalan-Valencian'
        self.lang_codes = list(languages.keys())
        lang_names = [f"{lang} ({languages[lang]})" for lang in self.lang_codes]
        
        # Add sorted language names to combo box
        sorted_items = sorted(zip(lang_names, self.lang_codes), key=lambda x: x[0])
        self.lang_names_to_codes = {name: code for name, code in sorted_items}
        self.lang_combo.addItems([name for name, _ in sorted_items])
        
        self.domain_combo = QComboBox()
        self.domain_combo.addItems(['com', 'co.uk', 'ca', 'co.in', 'ie', 'co.za'])
        lang_layout.addWidget(QLabel('Language:'))
        lang_layout.addWidget(self.lang_combo)
        lang_layout.addWidget(QLabel('Domain:'))
        lang_layout.addWidget(self.domain_combo)
        layout.addLayout(lang_layout)
        
        # Text input
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText('Enter text to convert to speech...')
        layout.addWidget(self.text_input)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton('Generate Speech')
        self.start_button.clicked.connect(self.start_speech_generation)
        button_layout.addWidget(self.start_button)
        
        self.pause_button = QPushButton('Pause')
        self.pause_button.clicked.connect(self.pause_resume_audio)
        self.pause_button.setEnabled(False)
        button_layout.addWidget(self.pause_button)
        
        self.save_button = QPushButton('Save')
        self.save_button.clicked.connect(self.save_audio)
        self.save_button.setEnabled(False)
        button_layout.addWidget(self.save_button)
        
        layout.addLayout(button_layout)
        
    def start_speech_generation(self):
        text = self.text_input.toPlainText()
        if not text:
            QMessageBox.warning(self, 'Error', 'Please enter some text')
            return
            
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Infinite progress
        self.start_button.setEnabled(False)
        
        # Create and start the worker thread
        self.worker = TTSWorker(
            text=text,
            lang=self.lang_names_to_codes[self.lang_combo.currentText()],
            tld=self.domain_combo.currentText()
        )
        self.worker.finished.connect(self.on_speech_generated)
        self.worker.error.connect(self.on_error)
        self.worker.start()
        
    def on_speech_generated(self, file_path: str):
        self.progress_bar.setVisible(False)
        self.start_button.setEnabled(True)
        self.current_sound = file_path
        self.pause_button.setEnabled(True)
        self.save_button.setEnabled(True)
        
        # Automatically play the generated audio
        pygame.mixer.music.load(self.current_sound)
        pygame.mixer.music.play()
        pygame.mixer.music.set_endevent(pygame.USEREVENT)
        self.is_playing = True
        
    def on_error(self, error_msg: str):
        self.progress_bar.setVisible(False)
        self.start_button.setEnabled(True)
        QMessageBox.critical(self, 'Error', f'Failed to generate speech: {error_msg}')
        
    def check_music_end(self):
        if not pygame.mixer.music.get_busy() and self.is_playing:
            self.is_playing = False
            self.pause_button.setEnabled(False)
            self.pause_button.setText('Pause')
            

        
    def pause_resume_audio(self):
        if self.is_playing:
            pygame.mixer.music.pause()
            self.is_playing = False
            self.pause_button.setText('Resume')
        else:
            pygame.mixer.music.unpause()
            self.is_playing = True
            self.pause_button.setText('Pause')
            
    def save_audio(self):
        if not self.current_sound:
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            'Save Audio File',
            '',
            'MP3 Files (*.mp3)'
        )
        
        if file_path:
            if not file_path.endswith('.mp3'):
                file_path += '.mp3'
            try:
                source_path = Path(self.current_sound)
                target_path = Path(file_path)
                source_path.rename(target_path)
                self.current_sound = str(target_path)
                QMessageBox.information(self, 'Success', 'Audio file saved successfully!')
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Failed to save file: {str(e)}')

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
