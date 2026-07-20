"""Conector opcional a una API de LLM (ej. OpenAI) para uso futuro.

El sistema NO depende de este módulo: el triage funciona por completo
con el motor de reglas de triage_engine.py. Esta función queda como
punto de extensión para, en el futuro, enriquecer la explicación con IA.
"""
import os
from typing import Optional

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")


def generar_explicacion_ia(sintoma_principal: str, descripcion: str) -> Optional[str]:
    """Punto de extensión futuro: si hay una API key configurada, aquí se
    podría llamar a un LLM para generar una explicación más detallada.
    Por ahora, si no hay API key, devuelve None y el sistema usa la
    explicación generada por el motor de reglas.
    """
    if not OPENAI_API_KEY:
        return None

    # Integración futura pendiente de implementar (fuera del alcance del MVP).
    return None
