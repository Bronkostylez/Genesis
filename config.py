"""Einstellungen und Pfade für den GENESIS-Host."""

from pathlib import Path

# ============================================================
# KONFIGURATION
# ============================================================

MODEL = "qwen2.5:7b"
OLLAMA_URL = "http://localhost:11434/api/chat"

BASE_DIR = Path(__file__).resolve().parent
GENESIS_DIR = BASE_DIR / "genesis_instance"

WINDOW_WIDTH = 900
WINDOW_HEIGHT = 760
CANVAS_HEIGHT = 360

MAX_VIEW_CHARS = 7000
MAX_FILES = 300
MAX_ACTION_HISTORY = 12

# Maximale Laufzeit eines von GENESIS ausgeführten Python-Programms
EXECUTION_TIMEOUT = 5

# Maximale Ausgabe eines ausgeführten Programms
MAX_EXECUTION_OUTPUT = 5000
