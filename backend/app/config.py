"""Configuración centralizada para la integración de IA (no expone secretos).

Soporta dos proveedores intercambiables mediante AI_PROVIDER:
- "openai": usa la API de OpenAI directamente.
- "gemini": usa Google Gemini a través de su capa de compatibilidad con el
  SDK de OpenAI (mismo cliente `openai.OpenAI`, solo cambia base_url,
  api_key y modelo). Por eso no se agrega ninguna dependencia nueva.
"""
import os
from dotenv import load_dotenv

load_dotenv()

AI_ENABLED = os.getenv("AI_ENABLED", "false").strip().lower() == "true"
AI_TIMEOUT_SECONDS = float(os.getenv("AI_TIMEOUT_SECONDS", "8"))

# Proveedor activo: "openai" (por defecto, compatibilidad hacia atrás) o "gemini"
AI_PROVIDER = os.getenv("AI_PROVIDER", "openai").strip().lower()

# --- OpenAI ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()

# --- Google Gemini (vía endpoint compatible con el SDK de OpenAI) ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-flash-latest").strip()
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"


def credenciales_activas() -> dict:
    """Devuelve las credenciales del proveedor seleccionado en AI_PROVIDER.

    `base_url` es None para OpenAI (usa el endpoint por defecto del SDK) y
    apunta al endpoint de compatibilidad de Gemini cuando corresponde.
    """
    if AI_PROVIDER == "gemini":
        return {
            "api_key": GEMINI_API_KEY,
            "model": GEMINI_MODEL,
            "base_url": GEMINI_BASE_URL,
        }
    return {
        "api_key": OPENAI_API_KEY,
        "model": OPENAI_MODEL,
        "base_url": None,
    }


def proveedor_activo_label() -> str:
    """Nombre legible del proveedor activo, para mostrar en /api/ai/status."""
    return "Gemini" if AI_PROVIDER == "gemini" else "OpenAI"


def ai_configurada() -> bool:
    """True solo si la IA está habilitada Y el proveedor activo tiene clave."""
    if not AI_ENABLED:
        return False
    return bool(credenciales_activas()["api_key"])
