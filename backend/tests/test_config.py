"""Pruebas de la selección de proveedor de IA (config.py)."""
from app import config


def test_proveedor_por_defecto_es_openai(monkeypatch):
    monkeypatch.setattr(config, "AI_PROVIDER", "openai")
    monkeypatch.setattr(config, "OPENAI_API_KEY", "clave-openai")
    monkeypatch.setattr(config, "OPENAI_MODEL", "gpt-4o-mini")

    credenciales = config.credenciales_activas()
    assert credenciales == {"api_key": "clave-openai", "model": "gpt-4o-mini", "base_url": None}
    assert config.proveedor_activo_label() == "OpenAI"


def test_proveedor_gemini_usa_su_endpoint_compatible(monkeypatch):
    monkeypatch.setattr(config, "AI_PROVIDER", "gemini")
    monkeypatch.setattr(config, "GEMINI_API_KEY", "clave-gemini")
    monkeypatch.setattr(config, "GEMINI_MODEL", "gemini-2.5-flash")

    credenciales = config.credenciales_activas()
    assert credenciales == {
        "api_key": "clave-gemini",
        "model": "gemini-2.5-flash",
        "base_url": config.GEMINI_BASE_URL,
    }
    assert config.proveedor_activo_label() == "Gemini"


def test_ai_configurada_false_si_ai_enabled_es_false(monkeypatch):
    monkeypatch.setattr(config, "AI_ENABLED", False)
    monkeypatch.setattr(config, "AI_PROVIDER", "gemini")
    monkeypatch.setattr(config, "GEMINI_API_KEY", "clave-gemini")
    assert config.ai_configurada() is False


def test_ai_configurada_false_si_falta_la_clave_del_proveedor_activo(monkeypatch):
    monkeypatch.setattr(config, "AI_ENABLED", True)
    monkeypatch.setattr(config, "AI_PROVIDER", "gemini")
    monkeypatch.setattr(config, "GEMINI_API_KEY", "")
    monkeypatch.setattr(config, "OPENAI_API_KEY", "clave-openai-que-no-debe-usarse")
    assert config.ai_configurada() is False


def test_ai_configurada_true_con_clave_del_proveedor_activo(monkeypatch):
    monkeypatch.setattr(config, "AI_ENABLED", True)
    monkeypatch.setattr(config, "AI_PROVIDER", "gemini")
    monkeypatch.setattr(config, "GEMINI_API_KEY", "clave-gemini")
    assert config.ai_configurada() is True
