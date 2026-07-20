"""Pruebas de integración del endpoint /triage contra una base de datos de
prueba aislada (nunca la real). Caso 12 del checklist, más verificaciones
de resiliencia del endpoint ante fallos de IA."""


def test_registro_se_guarda_en_postgresql(client, app_module, monkeypatch):
    monkeypatch.setattr(app_module, "analizar_con_ia", lambda datos: None)

    payload = {
        "nombre": "Paciente de Prueba Automatizada",
        "edad": 40,
        "sintoma_principal": "dolor abdominal",
        "descripcion": "dolor leve intermitente",
        "intensidad_dolor": 2,
        "fiebre": False,
        "dificultad_respirar": False,
        "sangrado": False,
        "perdida_conocimiento": False,
    }

    respuesta = client.post("/triage", json=payload)
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["nivel"] == "Verde"
    assert cuerpo["fuente_clasificacion"] == "REGLAS"

    listado = client.get("/triage")
    assert listado.status_code == 200
    ids = [registro["id"] for registro in listado.json()]
    assert cuerpo["id"] in ids


def test_endpoint_sigue_funcionando_cuando_la_ia_falla(client, app_module, monkeypatch):
    def _ia_que_falla(datos):
        raise RuntimeError("fallo simulado del proveedor de IA")

    monkeypatch.setattr(app_module, "analizar_con_ia", _ia_que_falla)

    payload = {
        "nombre": "Paciente con IA Caída",
        "edad": 50,
        "sintoma_principal": "tos",
        "descripcion": "tos seca",
        "intensidad_dolor": 3,
        "fiebre": False,
        "dificultad_respirar": False,
        "sangrado": False,
        "perdida_conocimiento": False,
    }

    respuesta = client.post("/triage", json=payload)
    assert respuesta.status_code == 200
    assert respuesta.json()["fuente_clasificacion"] == "REGLAS"


def test_nombre_no_llega_al_servicio_de_ia(client, app_module, monkeypatch):
    payloads_recibidos = []

    def _ia_espia(datos_clinicos):
        payloads_recibidos.append(datos_clinicos)
        return None

    monkeypatch.setattr(app_module, "analizar_con_ia", _ia_espia)

    payload = {
        "nombre": "Nombre Que No Debe Llegar A La IA",
        "edad": 22,
        "sintoma_principal": "mareo",
        "descripcion": "mareo leve",
        "intensidad_dolor": 1,
        "fiebre": False,
        "dificultad_respirar": False,
        "sangrado": False,
        "perdida_conocimiento": False,
    }

    respuesta = client.post("/triage", json=payload)
    assert respuesta.status_code == 200
    assert len(payloads_recibidos) == 1
    assert "nombre" not in payloads_recibidos[0]


def test_estado_ia_no_expone_la_clave(client, app_module, monkeypatch):
    from app import config as config_module

    monkeypatch.setattr(config_module, "AI_ENABLED", True)
    monkeypatch.setattr(config_module, "AI_PROVIDER", "openai")
    monkeypatch.setattr(config_module, "OPENAI_API_KEY", "clave-secreta-de-prueba")

    respuesta = client.get("/api/ai/status")
    assert respuesta.status_code == 200
    assert respuesta.json() == {"ai_enabled": True, "provider": "OpenAI", "configured": True}
    assert "clave-secreta-de-prueba" not in respuesta.text


def test_estado_ia_refleja_proveedor_gemini_sin_exponer_la_clave(client, app_module, monkeypatch):
    from app import config as config_module

    monkeypatch.setattr(config_module, "AI_ENABLED", True)
    monkeypatch.setattr(config_module, "AI_PROVIDER", "gemini")
    monkeypatch.setattr(config_module, "GEMINI_API_KEY", "clave-secreta-de-gemini")

    respuesta = client.get("/api/ai/status")
    assert respuesta.status_code == 200
    assert respuesta.json() == {"ai_enabled": True, "provider": "Gemini", "configured": True}
    assert "clave-secreta-de-gemini" not in respuesta.text


def test_estado_ia_gemini_sin_clave_no_configurado(client, app_module, monkeypatch):
    from app import config as config_module

    monkeypatch.setattr(config_module, "AI_ENABLED", True)
    monkeypatch.setattr(config_module, "AI_PROVIDER", "gemini")
    monkeypatch.setattr(config_module, "GEMINI_API_KEY", "")

    respuesta = client.get("/api/ai/status")
    assert respuesta.status_code == 200
    assert respuesta.json() == {"ai_enabled": True, "provider": "Gemini", "configured": False}


def test_dashboard_estadisticas_sigue_funcionando(client, app_module, monkeypatch):
    monkeypatch.setattr(app_module, "analizar_con_ia", lambda datos: None)

    client.post(
        "/triage",
        json={
            "nombre": "Paciente Dashboard",
            "edad": 60,
            "sintoma_principal": "dolor de pecho",
            "descripcion": "dolor intenso",
            "intensidad_dolor": 9,
            "fiebre": False,
            "dificultad_respirar": False,
            "sangrado": False,
            "perdida_conocimiento": False,
        },
    )

    respuesta = client.get("/estadisticas")
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["total"] >= 1
    assert cuerpo["naranja"] >= 1
