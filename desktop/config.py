"""
ExamPilot Configuration Module
GT InnoX LLP — Understand Questions. Learn the Answers.
"""

import os
from pathlib import Path

# Application Metadata
APP_NAME = "ExamPilot"
APP_TAGLINE = "Understand Questions. Learn the Answers."
APP_VERSION = "1.0.0"
COMPANY_NAME = "GT InnoX LLP"
COPYRIGHT = "© 2026 GT InnoX LLP. All rights reserved."

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
APP_DATA_DIR = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "ExamPilot"
APP_DATA_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_PATH = APP_DATA_DIR / "exampilot.db"
LOGS_DIR = APP_DATA_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR = APP_DATA_DIR / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

ASSETS_DIR = BASE_DIR / "assets"
ICONS_DIR = ASSETS_DIR / "icons"
LOGO_DIR = ASSETS_DIR / "logo"

# AI Inference Defaults (Ollama Local API)
DEFAULT_OLLAMA_HOST = "http://127.0.0.1:11434"
DEFAULT_PRIMARY_MODEL = "qwen2.5:7b-instruct"
DEFAULT_FALLBACK_MODEL = "qwen2.5:1.5b"
RECOMMENDED_MODELS = [
    {
        "name": "qwen2.5:7b-instruct",
        "label": "Qwen 2.5 7B Instruct (Recommended)",
        "ram_gb": 16,
        "disk_gb": 4.7,
        "description": "Best overall reasoning, nuanced option analysis & accurate explanations."
    },
    {
        "name": "qwen2.5:3b",
        "label": "Qwen 2.5 3B (Balanced)",
        "ram_gb": 12,
        "disk_gb": 2.0,
        "description": "Fast inference with good accuracy for mid-tier laptops."
    },
    {
        "name": "qwen2.5:1.5b",
        "label": "Qwen 2.5 1.5B (Lightweight)",
        "ram_gb": 8,
        "disk_gb": 1.0,
        "description": "Ultra-lightweight fallback for 8 GB RAM machines."
    },
    {
        "name": "llama3.2:3b",
        "label": "Llama 3.2 3B (Alternative)",
        "ram_gb": 8,
        "disk_gb": 2.0,
        "description": "Compact Meta model suitable for everyday practice."
    }
]

# Shortcut Configuration
DEFAULT_CAPTURE_HOTKEY = "<ctrl>+<shift>+q"
DEFAULT_CAPTURE_HOTKEY_STR = "Ctrl+Shift+Q"

# IPC / Native Messaging Bridge Port
LOCAL_IPC_PORT = 19842

# UI Theme Color Palette
COLORS = {
    "bg_dark": "#0B1020",
    "bg_secondary": "#111827",
    "bg_card": "#1E293B",
    "bg_card_hover": "#283548",
    "accent_primary": "#6366F1",
    "accent_primary_hover": "#4F46E5",
    "accent_secondary": "#06B6D4",
    "accent_secondary_hover": "#0891B2",
    "success": "#22C55E",
    "warning": "#F59E0B",
    "danger": "#EF4444",
    "text_primary": "#F8FAFC",
    "text_muted": "#94A3B8",
    "border_color": "#334155",
    "selection": "#6366F1"
}

