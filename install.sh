#!/bin/bash

# Create directories
sudo mkdir -p /usr/bin/
sudo mkdir -p /usr/share/applications/
sudo mkdir -p /usr/share/icons/hicolor/scalable/apps/
sudo mkdir -p /usr/share/gtts-gui/
sudo mkdir -p /usr/lib/python3/dist-packages/

# Install main program
sudo install -m 755 main.py /usr/bin/gtts-gui

# Install desktop file and icon
sudo install -m 644 gtts-gui.desktop /usr/share/applications/
sudo install -m 644 icons/gtts-gui.svg /usr/share/icons/hicolor/scalable/apps/

# Install other resources
sudo cp -r locale /usr/share/
sudo cp -r assets /usr/share/gtts-gui/
sudo cp supported_domains.txt /usr/share/gtts-gui/
sudo cp about_dialog.py /usr/lib/python3/dist-packages/

# Install Python dependencies
pip3 install -r requirements.txt

echo "Installation completed!"
