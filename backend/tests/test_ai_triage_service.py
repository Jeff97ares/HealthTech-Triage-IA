"""Pruebas del servicio de IA. La API de OpenAI siempre se simula (mock);
nunca se realizan llamadas reales ni pagadas. Casos 8, 9, 10 y 11 del
checklist."""
import json

import httpx
import openai
import pytest

from app import config
from app.services import ai_triage_service

DATOS_CLINICOS = {
    "edad": 30,
    "sintoma_principal": "dolor de cabeza",
    "descripcion": "dolor moderado desde ayer",
    "intensidad_dolor": 5,
    "fiebre": False,
    "dificultad_respirar": False,
    "sangrado": False,
    "perdida_conocimiento": False,
}


class _FakeMessage:
    def __init__(self, content):
        self.content = content


class _FakeChoice:
    def __init__(self, content):
        self.message = _FakeMessage(content)


class _FakeResponse:
    def __init__(self, content):
        self.choices = [_FakeChoice(content)]


def _cliente_falso(comportamiento):
    """Crea una clase que sustituye a openai.OpenAI; `comportamiento` es
    una función que recibe (self, *args, **kwargs) y devuelve la respuesta
    simulada o lanza una excepción."""

    class ClienteFalso:
        def __init__(self, *args, **kwargs):
            self.chat = self

        @property
        def completions(self):
            return self

        def create(self, *args, **kwargs):
            return comportamiento()

    return ClienteFalso


# --- Caso 8: el sistema funciona sin clave API ---
def test_sin_api_key_devuelve_none(monkeypatch):
    monkeypatch.setattr(config, "AI_ENABLED", True)
    monkeypatch.setattr(config, "OPENAI_API_KEY", "")
    assert ai_triage_service.analizar_con_ia(DATOS_CLINICOS) is None


def test_ai_deshabilitada_devuelve_none(monkeypatch):
    monkeypatch.setattr(config, "AI_ENABLED", False)
    monkeypatch.setattr(config, "OPENAI_API_KEY", "clave-de-prueba")
    assert ai_triage_service.analizar_con_ia(DATOS_CLINICOS) is None


# --- Caso 9: el sistema funciona cuando la API falla ---
def test_error_de_conexion_devuelve_none(monkeypatch):
    monkeypatch.setattr(config, "AI_ENABLED", True)
    monkeypatch.setattr(config, "OPENAI_API_KEY", "clave-de-prueba")

    def _fallar():
        peticion = httpx.Request("POST", "https://api.openai.com/v1/chat/completions")
        raise openai.APIConnectionError(request=peticion)

    monkeypatch.setattr(ai_triage_service, "OpenAI", _cliente_falso(_fallar))
    assert ai_triage_service.analizar_con_ia(DATOS_CLINICOS) is None


def test_error_inesperado_del_proveedor_devuelve_none(monkeypatch):
    monkeypatch.setattr(config, "AI_ENABLED", True)
    monkeypatch.setattr(config, "OPENAI_API_KEY", "clave-de-prueba")

    def _fallar():
        raise RuntimeError("límite de uso alcanzado (simulado)")

    monkeypatch.setattr(ai_triage_service, "OpenAI", _cliente_falso(_fallar))
    assert ai_triage_service.analizar_con_ia(DATOS_CLINICOS) is None


# --- Caso 10: una respuesta inválida de la IA activa el motor de respaldo ---
def test_json_invalido_devuelve_none(monkeypatch):
    monkeypatch.setattr(config, "AI_ENABLED", True)
    monkeypatch.setattr(config, "OPENAI_API_KEY", "clave-de-prueba")

    monkeypatch.setattr(
        ai_triage_service, "OpenAI", _cliente_falso(lambda: _FakeResponse("esto no es JSON"))
    )
    assert ai_triage_service.analizar_con_ia(DATOS_CLINICOS) is None


def test_json_sin_los_campos_requeridos_devuelve_none(monkeypatch):
    monkeypatch.setattr(config, "AI_ENABLED", True)
    monkeypatch.setattr(config, "OPENAI_API_KEY", "clave-de-prueba")

    contenido = json.dumps({"algo_no_esperado": True})
    monkeypatch.setattr(
        ai_triage_service, "OpenAI", _cliente_falso(lambda: _FakeResponse(contenido))
    )
    assert ai_triage_service.analizar_con_ia(DATOS_CLINICOS) is None


def test_nivel_no_permitido_devuelve_none(monkeypatch):
    monkeypatch.setattr(config, "AI_ENABLED", True)
    monkeypatch.setattr(config, "OPENAI_API_KEY", "clave-de-prueba")

    contenido = json.dumps(
        {
            "nivel_sugerido": "CRITICO",  # nivel no permitido
            "tipo_atencion": "VIRTUAL",
            "explicacion": "texto",
            "senales_alerta": [],
            "confianza": 0.5,
            "aviso": "aviso",
        }
    )
    monkeypatch.setattr(
        ai_triage_service, "OpenAI", _cliente_falso(lambda: _FakeResponse(contenido))
    )
    assert ai_triage_service.analizar_con_ia(DATOS_CLINICOS) is None


def test_respuesta_valida_se_convierte_en_iarespuesta(monkeypatch):
    monkeypatch.setattr(config, "AI_ENABLED", True)
    monkeypatch.setattr(config, "OPENAI_API_KEY", "clave-de-prueba")

    contenido = json.dumps(
        {
            "nivel_sugerido": "amarillo",
            "tipo_atencion": "virtual",
            "explicacion": "Síntomas leves sin señales de alarma.",
            "senales_alerta": [],
            "confianza": 0.7,
            "aviso": "Esta clasificación no reemplaza una evaluación médica.",
        }
    )
    monkeypatch.setattr(
        ai_triage_service, "OpenAI", _cliente_falso(lambda: _FakeResponse(contenido))
    )

    resultado = ai_triage_service.analizar_con_ia(DATOS_CLINICOS)
    assert resultado is not None
    assert resultado.nivel_sugerido == "AMARILLO"
    assert resultado.tipo_atencion == "VIRTUAL"


# --- Caso 11: el nombre del paciente nunca se envía al LLM ---
def test_payload_clinico_no_incluye_nombre():
    datos_con_nombre = {**DATOS_CLINICOS, "nombre": "Paciente Que No Debe Enviarse"}
    payload = ai_triage_service._payload_clinico(datos_con_nombre)
    assert "nombre" not in payload
    assert set(payload.keys()) == {
        "edad",
        "sintoma_principal",
        "descripcion",
        "intensidad_dolor",
        "fiebre",
        "dificultad_respirar",
        "sangrado",
        "perdida_conocimiento",
    }
