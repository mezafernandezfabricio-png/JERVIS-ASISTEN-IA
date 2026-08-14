# -*- mode: python ; coding: utf-8 -*-
"""
JARVIS AI Executable Build Specification
Compila JARVIS en un ejecutable binario protegido (.exe) para distribución comercial.
"""

import sys
import os
from pathlib import Path

block_cipher = None

BASE_DIR = Path(os.getcwd()).resolve()

# Archivos de datos y carpetas requeridos a incluir en la compilación
datas = [
    (str(BASE_DIR / "assets"), "assets"),
    (str(BASE_DIR / "config"), "config"),
    (str(BASE_DIR / "core"), "core"),
    (str(BASE_DIR / "memory"), "memory"),
    (str(BASE_DIR / "actions"), "actions"),
    (str(BASE_DIR / "agent"), "agent"),
]

if (BASE_DIR / "face.png").exists():
    datas.append((str(BASE_DIR / "face.png"), "."))

# Módulos ocultos y dependencias requeridas
hidden_imports = [
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
    'PyQt6.QtWebEngineWidgets',
    'PyQt6.QtWebEngineCore',
    'PyQt6.QtWebChannel',
    'PyQt6.QtNetwork',
    'PyQt6.QtPrintSupport',
    'qtawesome',
    'google.genai',
    'google.genai.types',
    'google.api_core',
    'google.auth',
    'openai',
    'sounddevice',
    'cffi',
    'vosk',
    'speech_recognition',
    'gtts',
    'edge_tts',
    'pygame',
    'cv2',
    'mediapipe',
    'pyautogui',
    'pyperclip',
    'pygetwindow',
    'pywinauto',
    'mss',
    'PIL',
    'PIL.Image',
    'win32com.client',
    'win32api',
    'win32con',
    'win32gui',
    'winshell',
    'win10toast',
    'pycaw',
    'comtypes',
    'fastapi',
    'uvicorn',
    'flask',
    'flask_socketio',
    'engineio.async_drivers.threading',
    'sqlite3',
    'ctypes',
    'docx',
    'docx2txt',
    'pptx',
    'fpdf',
    'openpyxl',
    'pandas',
    'numpy',
    'matplotlib',
    'qrcode',
    'cryptography',
    'rich',
    'psutil',
    'requests',
    'urllib3',
    'bs4',
    'duckduckgo_search',
    'yt_dlp',
    'youtube_transcript_api',
    'spotipy',
    'telebot',
    'openrgb',
    'keyboard',
    'send2trash',
    'speedtest',
    'pyunpack',
    'patool',
    'rarfile',
    'pypdf',
    'reportlab',
    'beta_config',
    'warden',
    'file_events',
    'ui',
    'actions',
    'agent',
    'core',
    'core.setup_wizard',
    'core.firebase_license',
    'core.license_verifier',
    'core.security_manager',
    'core.offline_voice',
    'core.tools_registry',
    'core.auto_updater',
]


a = Analysis(
    ['main.py'],
    pathex=[str(BASE_DIR)],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'unittest', 'PyQt6.QtQuick', 'PyQt6.QtQml', 'PyQt6.QtQuickWidgets', 'PyQt6.QtPositioning', 'PyQt6.QtSensors', 'PyQt6.QtTest', 'PyQt6.QtSql', 'PyQt6.Qt3DCore', 'PyQt6.QtBluetooth'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='XDS_AI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Ventana sin consola de comandos para apariencia limpia profesional
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(BASE_DIR / "assets" / "jarvis_icono.ico") if (BASE_DIR / "assets" / "jarvis_icono.ico").exists() else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='XDS_AI',
)