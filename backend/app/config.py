"""Configuración centralizada para la integración de IA (no expone secretos)."""
import os
from dotenv import load_dotenv

load_dotenv()

AI_ENABLED = os.getenv("AI_ENABLED", "false").strip().lower() == "true"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
AI_TIMEOUT_SECONDS = float(os.getenv("AI_TIMEOUT_SECONDS", "8"))


def ai_configurada() -> bool:
    """True solo si la IA está habilitada Y hay una clave API presente."""
    return AI_ENABLED and bool(OPENAI_API_KEY)
