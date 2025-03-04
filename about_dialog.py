"""
About dialog for the Google Text-to-Speech GUI Application
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QTextEdit, QDialogButtonBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from pathlib import Path
import builtins

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(builtins._("About Google Text-to-Speech"))
        self.setFixedSize(400, 300)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Title
        title = QLabel(builtins._("Google Text-to-Speech"))
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Version
        version = QLabel(builtins._("Version 1.0.2"))
        version.setAlignment(Qt.AlignCenter)
        layout.addWidget(version)
        
        # Description
        description = QLabel(
            builtins._("A simple and intuitive graphical interface for Google's "
            "Text-to-Speech service. Convert text to natural-sounding "
            "speech in multiple languages.")
        )
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignCenter)
        layout.addWidget(description)
        
        # Credits
        credits = QLabel(builtins._("Developed by LliureX\nUsing PyQt5 and gTTS (Google Text-to-Speech)\n© 2025 LliureX"))
        credits.setAlignment(Qt.AlignCenter)
        layout.addWidget(credits)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        license_button = QPushButton(builtins._("View License"))
        license_button.clicked.connect(self.show_license)
        button_layout.addWidget(license_button)
        
        close_button = QPushButton(builtins._("Close"))
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        
        # Add some spacing
        layout.addStretch()
    
    def show_license(self):
        dialog = QDialog(self)
        dialog.setWindowTitle(builtins._("MIT License"))
        dialog.setFixedSize(500, 400)
        
        layout = QVBoxLayout(dialog)
        
        # License text display
        license_text = QTextEdit()
        license_text.setReadOnly(True)
        
        # Read and display license file
        try:
            # First try the installed package location
            license_paths = [
                Path('/usr/share/doc/gtts-gui/copyright'),  # Debian package location
                Path(__file__).parent.parent.parent.parent / 'LICENSE',  # Development location
                Path(__file__).parent / 'LICENSE'  # Old location (fallback)
            ]
            
            license_content = None
            for path in license_paths:
                if path.exists():
                    license_content = path.read_text()
                    break
            
            if license_content:
                license_text.setText(license_content)
            else:
                license_text.setText(builtins._("License file not found."))
        except Exception as e:
            license_text.setText(builtins._(f"Error loading license file: {str(e)}"))
        
        layout.addWidget(license_text)
        
        # OK button
        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(dialog.accept)
        layout.addWidget(buttons)
        
        dialog.exec()
