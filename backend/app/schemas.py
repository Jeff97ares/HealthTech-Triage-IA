"""Esquemas Pydantic para validación de entrada/salida de la API."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


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


class Estadisticas(BaseModel):
    total: int
    rojo: int
    naranja: int
    amarillo: int
    verde: int
