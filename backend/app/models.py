"""Modelo de la tabla triage_records."""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func

from .database import Base


class TriageRecord(Base):
    __tablename__ = "triage_records"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False)
    edad = Column(Integer, nullable=False)
    sintoma_principal = Column(String(200), nullable=False)
    descripcion = Column(String(1000), nullable=True)
    intensidad_dolor = Column(Integer, nullable=False)
    fiebre = Column(Boolean, nullable=False, default=False)
    dificultad_respirar = Column(Boolean, nullable=False, default=False)
    sangrado = Column(Boolean, nullable=False, default=False)
    perdida_conocimiento = Column(Boolean, nullable=False, default=False)
    nivel = Column(String(20), nullable=False)
    color = Column(String(20), nullable=False)
    recomendacion = Column(String(300), nullable=False)
    explicacion = Column(String(500), nullable=False)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
