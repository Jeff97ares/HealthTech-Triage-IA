"""Pruebas del motor híbrido (reglas + IA). Casos 6 y 7 del checklist."""
from app.triage_engine import detalle_por_nivel
from app.triage_hibrido import clasificar_triage_hibrido
from app.services.ai_triage_service import IARespuesta


def _resultado_reglas(nivel: str) -> dict:
    detalle = detalle_por_nivel(nivel)
    return {
        "nivel": nivel,
        "color": detalle["color"],
        "recomendacion": detalle["recomendacion"],
        "explicacion": "explicación de prueba del motor de reglas",
    }


def _respuesta_ia(nivel_sugerido: str, senales=None) -> IARespuesta:
    return IARespuesta(
        nivel_sugerido=nivel_sugerido,
        tipo_atencion="VIRTUAL",
        explicacion="explicación de prueba de la IA",
        senales_alerta=senales or [],
        confianza=0.8,
        aviso="Esta clasificación no reemplaza una evaluación médica.",
    )


def test_ia_no_puede_reducir_una_clasificacion_rojo():
    resultado = clasificar_triage_hibrido(_resultado_reglas("Rojo"), _respuesta_ia("AMARILLO"))
    assert resultado["clasificacion_final"] == "Rojo"
    assert resultado["clasificacion_reglas"] == "Rojo"
    assert resultado["clasificacion_ia"] == "Amarillo"
    assert resultado["fuente_clasificacion"] == "HIBRIDA"
    assert resultado["tipo_atencion"] == "EMERGENCIA"


def test_ia_puede_aumentar_la_prioridad():
    resultado = clasificar_triage_hibrido(_resultado_reglas("Amarillo"), _respuesta_ia("NARANJA"))
    assert resultado["clasificacion_final"] == "Naranja"
    assert resultado["clasificacion_reglas"] == "Amarillo"
    assert resultado["clasificacion_ia"] == "Naranja"


def test_reglas_y_ia_coinciden_en_verde():
    resultado = clasificar_triage_hibrido(_resultado_reglas("Verde"), _respuesta_ia("VERDE"))
    assert resultado["clasificacion_final"] == "Verde"
    assert resultado["fuente_clasificacion"] == "HIBRIDA"


def test_ia_no_disponible_usa_solo_reglas():
    resultado = clasificar_triage_hibrido(_resultado_reglas("Amarillo"), None)
    assert resultado["clasificacion_final"] == "Amarillo"
    assert resultado["clasificacion_ia"] is None
    assert resultado["fuente_clasificacion"] == "REGLAS"
