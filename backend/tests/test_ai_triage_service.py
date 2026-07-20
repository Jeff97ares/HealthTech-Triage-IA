"""Pruebas del servicio de IA. La API del proveedor (OpenAI o Gemini)
siempre se simula (mock); nunca se realizan llamadas reales ni pagadas.
Casos 8, 9, 10 y 11 del checklist, más los casos de Gemini."""
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


# ============================================================
# Proveedor Gemini (AI_PROVIDER=gemini), vía compatibilidad OpenAI.
# Mismos escenarios que arriba, pero seleccionando el proveedor Gemini.
# ============================================================


def _preparar_gemini(monkeypatch, clave="clave-gemini-de-prueba"):
    monkeypatch.setattr(config, "AI_ENABLED", True)
    monkeypatch.setattr(config, "AI_PROVIDER", "gemini")
    monkeypatch.setattr(config, "GEMINI_API_KEY", clave)
    monkeypatch.setattr(config, "GEMINI_MODEL", "gemini-2.5-flash")


def test_gemini_respuesta_valida_se_convierte_en_iarespuesta_y_usa_su_endpoint(monkeypatch):
    _preparar_gemini(monkeypatch)

    contenido = json.dumps(
        {
            "nivel_sugerido": "naranja",
            "tipo_atencion": "presencial",
            "explicacion": "Dolor intenso reportado por el paciente.",
            "senales_alerta": ["dolor intenso"],
            "confianza": 0.75,
            "aviso": "Esta clasificación no reemplaza una evaluación médica.",
        }
    )

    llamadas_al_cliente = []

    class ClienteFalsoGemini:
        def __init__(self, **kwargs):
            llamadas_al_cliente.append(kwargs)
            self.chat = self

        @property
        def completions(self):
            return self

        def create(self, *args, **kwargs):
            return _FakeResponse(contenido)

    monkeypatch.setattr(ai_triage_service, "OpenAI", ClienteFalsoGemini)

    resultado = ai_triage_service.analizar_con_ia(DATOS_CLINICOS)
    assert resultado is not None
    assert resultado.nivel_sugerido == "NARANJA"
    # Confirma que se usó la clave/endpoint de Gemini, no los de OpenAI.
    assert llamadas_al_cliente[0]["api_key"] == "clave-gemini-de-prueba"
    assert llamadas_al_cliente[0]["base_url"] == config.GEMINI_BASE_URL


def test_gemini_cuota_excedida_devuelve_none(monkeypatch):
    _preparar_gemini(monkeypatch)

    def _fallar():
        peticion = httpx.Request(
            "POST", "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
        )
        respuesta_falsa = httpx.Response(
            429, request=peticion, json={"error": {"message": "quota exceeded"}}
        )
        raise openai.RateLimitError(message="quota exceeded", response=respuesta_falsa, body=None)

    monkeypatch.setattr(ai_triage_service, "OpenAI", _cliente_falso(_fallar))
    assert ai_triage_service.analizar_con_ia(DATOS_CLINICOS) is None


def test_gemini_clave_invalida_devuelve_none(monkeypatch):
    _preparar_gemini(monkeypatch, clave="clave-gemini-invalida")

    def _fallar():
        peticion = httpx.Request(
            "POST", "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
        )
        respuesta_falsa = httpx.Response(
            401, request=peticion, json={"error": {"message": "invalid api key"}}
        )
        raise openai.AuthenticationError(message="invalid api key", response=respuesta_falsa, body=None)

    monkeypatch.setattr(ai_triage_service, "OpenAI", _cliente_falso(_fallar))
    assert ai_triage_service.analizar_con_ia(DATOS_CLINICOS) is None


def test_gemini_json_invalido_activa_respaldo_de_reglas(monkeypatch):
    _preparar_gemini(monkeypatch)

    monkeypatch.setattr(
        ai_triage_service, "OpenAI", _cliente_falso(lambda: _FakeResponse("esto no es JSON"))
    )
    assert ai_triage_service.analizar_con_ia(DATOS_CLINICOS) is None


def test_gemini_sin_clave_configurada_usa_reglas(monkeypatch):
    """AI_PROVIDER=gemini pero GEMINI_API_KEY vacío: ai_configurada() debe
    devolver False y ni siquiera intentar la llamada."""
    monkeypatch.setattr(config, "AI_ENABLED", True)
    monkeypatch.setattr(config, "AI_PROVIDER", "gemini")
    monkeypatch.setattr(config, "GEMINI_API_KEY", "")
    assert ai_triage_service.analizar_con_ia(DATOS_CLINICOS) is None


def test_gemini_no_envia_nombre_del_paciente(monkeypatch):
    # _payload_clinico es independiente del proveedor; se reafirma aquí
    # explícitamente para el caso de uso con Gemini.
    monkeypatch.setattr(config, "AI_PROVIDER", "gemini")
    datos_con_nombre = {**DATOS_CLINICOS, "nombre": "Paciente Que No Debe Enviarse"}
    payload = ai_triage_service._payload_clinico(datos_con_nombre)
    assert "nombre" not in payload
