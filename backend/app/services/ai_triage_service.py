"""Servicio de clasificación asistida por IA para HealthTech Triage.

Soporta dos proveedores intercambiables (ver AI_PROVIDER en config.py):
OpenAI directamente, o Google Gemini a través de su endpoint compatible
con el SDK de OpenAI (mismo cliente `openai.OpenAI`, solo cambia
base_url/api_key/modelo). Por eso todo este archivo usa un único cliente
y un único bloque de manejo de errores para ambos proveedores.

Este servicio es un apoyo OPCIONAL sobre el motor de reglas
(triage_engine.py). Si la IA no está configurada, falla, tarda demasiado
o responde algo inválido, esta función devuelve None y el sistema sigue
funcionando únicamente con las reglas. Nunca deja el formulario
inutilizable ni propaga una excepción hacia el endpoint que la llama.

Privacidad: solo se envían datos clínicos (edad, síntomas, dolor, señales
de alarma). Nunca se envía el nombre del paciente ni otro identificador.
"""
import json
import logging
from typing import List, Literal, Optional

import openai
from openai import OpenAI
from pydantic import BaseModel, Field, ValidationError, field_validator

from .. import config

logger = logging.getLogger("healthtech.ai_triage")

MENSAJE_SISTEMA = (
    "Eres un asistente de apoyo para un prototipo académico de triage "
    "médico. No diagnosticas enfermedades ni recomiendas medicamentos, "
    "dosis ni tratamientos. Debes clasificar el caso ÚNICAMENTE en uno de "
    "estos cuatro niveles: ROJO, NARANJA, AMARILLO o VERDE. Sé conservador "
    "ante cualquier signo grave: ante la duda, elige el nivel más alto. "
    "Si detectas peligro evidente (dificultad para respirar, sangrado "
    "importante, pérdida de conocimiento, dolor extremo), recomienda "
    "atención de EMERGENCIA. Responde ÚNICAMENTE con un objeto JSON con "
    "exactamente estas claves: nivel_sugerido (ROJO|NARANJA|AMARILLO|VERDE), "
    "tipo_atencion (EMERGENCIA|PRESENCIAL|VIRTUAL), explicacion (texto "
    "breve y comprensible, máximo 300 caracteres), senales_alerta (lista "
    "de hasta 5 textos breves con las señales identificadas), confianza "
    "(número entre 0.0 y 1.0), y aviso (texto indicando que esta "
    "clasificación no reemplaza una evaluación médica). No incluyas texto "
    "fuera del JSON. Tu resultado es orientativo y siempre requiere "
    "revisión profesional."
)


class IARespuesta(BaseModel):
    """Salida validada del LLM. Cualquier campo fuera de rango o con un
    valor no permitido hace que la validación falle, y el llamador debe
    tratarlo igual que una IA no disponible (usar solo reglas)."""

    nivel_sugerido: Literal["ROJO", "NARANJA", "AMARILLO", "VERDE"]
    tipo_atencion: Literal["EMERGENCIA", "PRESENCIAL", "VIRTUAL"]
    explicacion: str = Field(max_length=500)
    senales_alerta: List[str] = Field(default_factory=list)
    confianza: float = Field(ge=0.0, le=1.0)
    aviso: str = "Esta clasificación no reemplaza una evaluación médica."

    @field_validator("nivel_sugerido", "tipo_atencion", mode="before")
    @classmethod
    def _normalizar_mayusculas(cls, valor):
        if isinstance(valor, str):
            return valor.strip().upper()
        return valor

    @field_validator("senales_alerta", mode="before")
    @classmethod
    def _limitar_senales(cls, valor):
        if not isinstance(valor, list):
            return []
        return [str(item)[:120] for item in valor[:5]]

    @field_validator("explicacion", mode="before")
    @classmethod
    def _limitar_explicacion(cls, valor):
        return str(valor)[:500] if valor is not None else ""


def _payload_clinico(datos: dict) -> dict:
    """Arma el payload clínico enviado al LLM. Solo datos clínicos: nunca
    el nombre del paciente ni ningún otro identificador personal."""
    return {
        "edad": datos["edad"],
        "sintoma_principal": str(datos["sintoma_principal"])[:200],
        "descripcion": str(datos.get("descripcion") or "")[:1000],
        "intensidad_dolor": datos["intensidad_dolor"],
        "fiebre": bool(datos["fiebre"]),
        "dificultad_respirar": bool(datos["dificultad_respirar"]),
        "sangrado": bool(datos["sangrado"]),
        "perdida_conocimiento": bool(datos["perdida_conocimiento"]),
    }


def analizar_con_ia(datos: dict) -> Optional[IARespuesta]:
    """Solicita una clasificación sugerida al LLM.

    Devuelve None si: la IA está deshabilitada o sin clave configurada,
    falla la conexión/autenticación, se agota el tiempo de espera, se
    alcanza un límite de uso, el modelo no existe, o la respuesta no
    cumple el esquema esperado. Nunca lanza una excepción.
    """
    if not config.ai_configurada():
        return None

    payload = _payload_clinico(datos)
    credenciales = config.credenciales_activas()
    proveedor = config.proveedor_activo_label()

    try:
        argumentos_cliente = {
            "api_key": credenciales["api_key"],
            "timeout": config.AI_TIMEOUT_SECONDS,
        }
        if credenciales["base_url"]:
            argumentos_cliente["base_url"] = credenciales["base_url"]

        cliente = OpenAI(**argumentos_cliente)

        respuesta = cliente.chat.completions.create(
            model=credenciales["model"],
            messages=[
                {"role": "system", "content": MENSAJE_SISTEMA},
                {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
            ],
            response_format={"type": "json_object"},
            timeout=config.AI_TIMEOUT_SECONDS,
        )

        contenido = respuesta.choices[0].message.content or ""
        datos_ia = json.loads(contenido)
        return IARespuesta.model_validate(datos_ia)

    except openai.AuthenticationError:
        logger.warning("IA no disponible (%s): clave inválida o no autorizada.", proveedor)
    except openai.RateLimitError:
        logger.warning("IA no disponible (%s): límite de uso o cuota alcanzada.", proveedor)
    except openai.NotFoundError:
        logger.warning("IA no disponible (%s): el modelo configurado no está disponible.", proveedor)
    except openai.APITimeoutError:
        logger.warning("IA no disponible (%s): tiempo de espera agotado.", proveedor)
    except openai.APIConnectionError:
        logger.warning("IA no disponible (%s): error de conexión.", proveedor)
    except openai.APIStatusError as error:
        logger.warning("IA no disponible (%s): error del proveedor (%s).", proveedor, error.status_code)
    except (json.JSONDecodeError, ValidationError):
        logger.warning("IA no disponible (%s): la respuesta no tiene el formato esperado.", proveedor)
    except Exception:
        logger.warning("IA no disponible (%s): error inesperado al consultar el modelo.", proveedor)

    return None
