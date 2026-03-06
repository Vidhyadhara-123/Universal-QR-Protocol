# Universal QR Code Generator

A professional Windows desktop application to generate QR codes for URLs, WiFi, Emails, and more.

## Features
- Support for Website URLs, Text, WiFi, Email, Code snippets.
- Live QR Code preview.
- Customizable colors and sizes.
- Export as PNG, JPG, or SVG.
- Copy to clipboard support (requires `pywin32`).

## Requirements
- Python 3.x
- Windows 10/11

## Setup Instructions

1. **Clone or Extract** the project folder.
2. **Open PowerShell** in the project directory.
3. **Install Dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```
   *(Optional) For copy-to-clipboard support:*
   ```powershell
   pip install pywin32
   ```
4. **Run the Application**:
   ```powershell
   python main.py
   ```

## Folder Structure
- `main.py`: Entry point.
- `ui.py`: Tkinter UI layout and event handling.
- `qr_logic.py`: Backend logic for QR generation.
- `requirements.txt`: List of required libraries.
