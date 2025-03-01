"""
About dialog for the Google Text-to-Speech GUI Application
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QTextEdit, QDialogButtonBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from pathlib import Path

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About Google Text-to-Speech")
        self.setFixedSize(400, 300)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Title
        title = QLabel("Google Text-to-Speech")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Version
        version = QLabel("Version 1.0")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version)
        
        # Description
        description = QLabel(
            "A simple and intuitive graphical interface for Google's "
            "Text-to-Speech service. Convert text to natural-sounding "
            "speech in multiple languages."
        )
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(description)
        
        # Credits
        credits = QLabel(
            "\nDeveloped by LliureX\n"
            "Using PyQt6 and gTTS (Google Text-to-Speech)\n"
            "© 2024 LliureX"
        )
        credits.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(credits)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        license_button = QPushButton("View License")
        license_button.clicked.connect(self.show_license)
        button_layout.addWidget(license_button)
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        
        # Add some spacing
        layout.addStretch()
    
    def show_license(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("MIT License")
        dialog.setFixedSize(500, 400)
        
        layout = QVBoxLayout(dialog)
        
        # License text display
        license_text = QTextEdit()
        license_text.setReadOnly(True)
        
        # Read and display license file
        try:
            license_path = Path(__file__).parent / 'LICENSE'
            license_content = license_path.read_text()
            license_text.setText(license_content)
        except Exception as e:
            license_text.setText("Error loading license file.")
        
        layout.addWidget(license_text)
        
        # OK button
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(dialog.accept)
        layout.addWidget(buttons)
        
        dialog.exec()
