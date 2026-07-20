"""Esquemas Pydantic para validación de entrada/salida de la API."""
import json
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator


class TriageInput(BaseModel):
    """Datos que envía el formulario de síntomas. Validación básica de rangos."""

    nombre: str = Field(min_length=2, max_length=150)
    edad: int = Field(ge=0, le=120)
    sintoma_principal: str = Field(min_length=2, max_length=200)
    descripcion: str = Field(default="", max_length=1000)
    intensidad_dolor: int = Field(ge=1, le=10)
    fiebre: bool = False
    dificultad_respirar: bool = False
    sangrado: bool = False
    perdida_conocimiento: bool = False


class TriageOutput(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    edad: int
    sintoma_principal: str
    descripcion: Optional[str] = None
    intensidad_dolor: int
    fiebre: bool
    dificultad_respirar: bool
    sangrado: bool
    perdida_conocimiento: bool
    nivel: str
    color: str
    recomendacion: str
    explicacion: str
    fecha_creacion: datetime

    # Campos del motor híbrido (reglas + IA). Todos opcionales para no
    # romper registros creados antes de esta funcionalidad.
    clasificacion_reglas: Optional[str] = None
    clasificacion_ia: Optional[str] = None
    fuente_clasificacion: str = "REGLAS"
    explicacion_ia: Optional[str] = None
    tipo_atencion: Optional[str] = None
    senales_alerta: Optional[List[str]] = None
    confianza_ia: Optional[float] = None

    @field_validator("senales_alerta", mode="before")
    @classmethod
    def _parsear_senales_alerta(cls, valor):
        """La columna se guarda como texto JSON; se convierte a lista para
        el frontend. Si el valor no es un JSON válido, se ignora."""
        if valor is None or isinstance(valor, list):
            return valor
        if isinstance(valor, str):
            try:
                datos = json.loads(valor)
                return datos if isinstance(datos, list) else None
            except json.JSONDecodeError:
                return None
        return None


class Estadisticas(BaseModel):
    total: int
    rojo: int
    naranja: int
    amarillo: int
    verde: int


class EstadoIA(BaseModel):
    ai_enabled: bool
    provider: str = "OpenAI"
    configured: bool
