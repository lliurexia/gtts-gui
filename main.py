"""
Google Text-to-Speech GUI Application
Using PyQt6 and gTTS
"""

import sys
from pathlib import Path
from typing import Optional
import pygame
import gettext
import os

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QComboBox, QTextEdit, QPushButton, QFileDialog, QProgressBar,
    QLabel, QMessageBox
)
from about_dialog import AboutDialog
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QIcon
from pathlib import Path
from gtts import gTTS
import gtts.lang
import os
import locale

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

def setup_translations():
    # Get the system language
    lang = None
    lang_var = os.getenv('LANGUAGE')
    if lang_var:
        # Handle Valencian Catalan special case
        if lang_var.startswith('ca@valencia'):
            lang = 'ca'
        else:
            lang = lang_var.split(':')[0].split('_')[0].split('@')[0]
    
    if not lang:
        lang_var = os.getenv('LANG')
        if lang_var:
            lang = lang_var.split('_')[0]
    
    if not lang:
        lang = 'en'
    
    # Set up translations
    localedir = os.path.join(os.path.dirname(__file__), 'locale')
    try:
        translation = gettext.translation('messages', localedir=localedir, languages=[lang])
        translation.install()
    except FileNotFoundError:
        # Fallback to English
        gettext.install('messages')

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(_('Google Text-to-Speech'))
        self.setMinimumSize(600, 400)
        
        # Set window icon
        icon_path = Path(__file__).parent / 'icons' / 'app.svg'
        self.setWindowIcon(QIcon(str(icon_path)))
        
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
        self.lang_combo.setFixedWidth(250)  # Set fixed width for language dropdown
        
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
        display_names = [name for name, _ in sorted_items]
        self.lang_combo.addItems(display_names)
        
        # Get system language
        try:
            # Try multiple methods to get system language
            system_lang = None
            # Try LANGUAGE env var first (Ubuntu specific)
            lang_var = os.getenv('LANGUAGE')
            if lang_var:
                # Handle Valencian Catalan special case
                if lang_var.startswith('ca@valencia'):
                    system_lang = 'ca'
                else:
                    system_lang = lang_var.split(':')[0].split('_')[0].split('@')[0]
            # Try LANG env var next
            if not system_lang:
                lang_var = os.getenv('LANG')
                if lang_var:
                    system_lang = lang_var.split('_')[0]
            # Finally try locale
            if not system_lang:
                try:
                    system_lang = locale.getdefaultlocale()[0].split('_')[0]
                except (IndexError, AttributeError):
                    pass
            print(f'Detected system language: {system_lang}')
            # Find the display name that matches the system language code
            for display_name, lang_code in sorted_items:
                if lang_code == system_lang:
                    self.lang_combo.setCurrentText(display_name)
                    break
        except (IndexError, AttributeError):
            # If something goes wrong, keep the first language as default
            pass
        
        # Language-specific domain mappings
        self.lang_domains = {
            'en': {  # English
                'United States': 'us',
                'United Kingdom': 'co.uk',
                'Australia': 'com.au',
                'Canada': 'ca',
                'India': 'co.in',
                'Ireland': 'ie',
                'South Africa': 'co.za',
                'Nigeria': 'com.ng'
            },
            'es': {  # Spanish
                'Spain': 'es',
                'Mexico': 'com.mx',
                'United States': 'us'
            },
            'fr': {  # French
                'France': 'fr',
                'Canada': 'ca'
            },
            'pt': {  # Portuguese
                'Portugal': 'pt',
                'Brazil': 'com.br'
            }
        }
        
        # Domain selection
        self.domain_combo = QComboBox()
        self.domain_combo.setFixedWidth(150)  # Set fixed width for accent dropdown
        self.domain_combo.setEnabled(False)  # Disabled by default
        
        # Connect language change to domain update
        self.lang_combo.currentTextChanged.connect(self.update_domains)
        
        # Initial domain setup
        self.update_domains(self.lang_combo.currentText())
        lang_layout.addWidget(QLabel(_('Language:')))
        lang_layout.addWidget(self.lang_combo)
        lang_layout.addWidget(QLabel(_('Accent:')))
        lang_layout.addWidget(self.domain_combo)
        
        # Add About button to language layout with some spacing
        lang_layout.addSpacing(20)
        self.about_button = QPushButton(_('About'))
        self.about_button.clicked.connect(self.show_about_dialog)
        lang_layout.addWidget(self.about_button)
        layout.addLayout(lang_layout)
        
        # Text input
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText(_('Enter text to convert to speech...'))
        layout.addWidget(self.text_input)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton(_('Generate Speech'))
        self.start_button.clicked.connect(self.start_speech_generation)
        button_layout.addWidget(self.start_button)
        
        self.pause_button = QPushButton(_('Pause'))
        self.pause_button.clicked.connect(self.pause_resume_audio)
        self.pause_button.setEnabled(False)
        button_layout.addWidget(self.pause_button)
        
        self.save_button = QPushButton(_('Save'))
        self.save_button.clicked.connect(self.save_audio)
        self.save_button.setEnabled(False)
        button_layout.addWidget(self.save_button)
        

        
        layout.addLayout(button_layout)
        
    def start_speech_generation(self):
        text = self.text_input.toPlainText()
        if not text:
            QMessageBox.warning(self, _('Error'), _('Please enter some text'))
            return
            
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Infinite progress
        self.start_button.setEnabled(False)
        
        # Create and start the worker thread
        self.worker = TTSWorker(
            text=text,
            lang=self.lang_names_to_codes[self.lang_combo.currentText()],
            tld=self.lang_domains.get(self.lang_names_to_codes[self.lang_combo.currentText()], {}).get(self.domain_combo.currentText(), 'com')
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
        
    def update_domains(self, lang_name: str):
        # Clear current items
        self.domain_combo.clear()
        
        # Get language code from the display name
        lang_code = self.lang_names_to_codes[lang_name]
        
        # If language has specific domains, populate and enable
        if lang_code in self.lang_domains:
            domains = self.lang_domains[lang_code]
            self.domain_combo.addItems(domains.keys())
            self.domain_combo.setEnabled(True)
        else:
            # For languages without specific domains, use default and disable
            self.domain_combo.addItem('Default')
            self.domain_combo.setEnabled(False)
    
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
            
    def show_about_dialog(self):
        dialog = AboutDialog(self)
        dialog.exec()
    
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
    
    # Set application icon
    icon_path = Path(__file__).parent / 'icons' / 'app.svg'
    app.setWindowIcon(QIcon(str(icon_path)))
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    setup_translations()
    main()
