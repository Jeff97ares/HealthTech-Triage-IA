"""Motor híbrido: combina el resultado del motor de reglas (fuente de
seguridad, siempre presente) con la sugerencia opcional de la IA.

Principio de mayor seguridad: la IA nunca puede reducir la prioridad
detectada por las reglas. El nivel final es siempre el más severo entre
ambos resultados.
"""
from typing import Optional

from .triage_engine import detalle_por_nivel
from .services.ai_triage_service import IARespuesta

# Orden de severidad: menor índice = más urgente.
PRIORIDAD = {"Rojo": 0, "Naranja": 1, "Amarillo": 2, "Verde": 3}

# La IA responde en mayúsculas (ROJO, NARANJA...); el resto del sistema
# usa las etiquetas en formato título (Rojo, Naranja...) por compatibilidad
# con los registros y el dashboard existentes.
_A_TITULO = {"ROJO": "Rojo", "NARANJA": "Naranja", "AMARILLO": "Amarillo", "VERDE": "Verde"}


def _tipo_atencion_por_nivel(nivel_final: str, senales_alerta: list) -> str:
    """Determina el tipo de atención de forma conservadora a partir del
    nivel FINAL ya calculado (no delega esta decisión a la IA)."""
    if nivel_final == "Rojo":
        return "EMERGENCIA"
    if nivel_final == "Naranja":
        return "PRESENCIAL"
    if nivel_final == "Amarillo":
        return "VIRTUAL" if not senales_alerta else "PRESENCIAL"
    return "VIRTUAL"  # Verde


def clasificar_triage_hibrido(resultado_reglas: dict, resultado_ia: Optional[IARespuesta]) -> dict:
    """Combina el resultado de reglas con la sugerencia de IA (si existe).

    - resultado_reglas: el dict devuelto por triage_engine.clasificar_triage().
    - resultado_ia: una IARespuesta validada, o None si la IA no respondió
      o no está disponible.

    Devuelve un dict con la clasificación final y toda la trazabilidad
    (reglas, IA, fuente) para guardar en la base de datos y mostrar en el
    frontend.
    """
    clasificacion_reglas = resultado_reglas["nivel"]

    if resultado_ia is None:
        nivel_final = clasificacion_reglas
        detalle = detalle_por_nivel(nivel_final)
        return {
            "clasificacion_reglas": clasificacion_reglas,
            "clasificacion_ia": None,
            "clasificacion_final": nivel_final,
            "fuente_clasificacion": "REGLAS",
            "nivel": nivel_final,
            "color": detalle["color"],
            "recomendacion": detalle["recomendacion"],
            "explicacion": resultado_reglas["explicacion"],
            "explicacion_ia": None,
            "tipo_atencion": _tipo_atencion_por_nivel(nivel_final, []),
            "senales_alerta": [],
            "confianza_ia": None,
        }

    clasificacion_ia = _A_TITULO[resultado_ia.nivel_sugerido]

    # Principio de mayor seguridad: se elige el nivel más severo (menor
    # índice de prioridad). La IA nunca puede bajar la prioridad de reglas.
    nivel_final = min(
        clasificacion_reglas,
        clasificacion_ia,
        key=lambda nivel: PRIORIDAD[nivel],
    )

    detalle = detalle_por_nivel(nivel_final)

    if nivel_final == clasificacion_reglas:
        explicacion_final = resultado_reglas["explicacion"]
    else:
        explicacion_final = (
            f"El motor de reglas indicó {clasificacion_reglas}, y la "
            f"clasificación asistida por IA elevó la prioridad a {nivel_final} "
            "por señales adicionales identificadas."
        )

    return {
        "clasificacion_reglas": clasificacion_reglas,
        "clasificacion_ia": clasificacion_ia,
        "clasificacion_final": nivel_final,
        "fuente_clasificacion": "HIBRIDA",
        "nivel": nivel_final,
        "color": detalle["color"],
        "recomendacion": detalle["recomendacion"],
        "explicacion": explicacion_final,
        "explicacion_ia": resultado_ia.explicacion,
        "tipo_atencion": _tipo_atencion_por_nivel(nivel_final, resultado_ia.senales_alerta),
        "senales_alerta": resultado_ia.senales_alerta,
        "confianza_ia": resultado_ia.confianza,
    }
