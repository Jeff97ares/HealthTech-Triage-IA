"""API REST de HealthTech - Plataforma de Triage Inteligente con IA."""
import os
from typing import List

from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import models, schemas
from .database import Base, engine, get_db
from .triage_engine import clasificar_triage

load_dotenv()

# Crea la tabla triage_records automáticamente al iniciar el backend
Base.metadata.create_all(bind=engine)

app = FastAPI(title="HealthTech - Plataforma de Triage Inteligente con IA")

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def raiz():
    """Confirma que la API está funcionando."""
    return {"mensaje": "API de HealthTech Triage funcionando correctamente."}


@app.post("/triage", response_model=schemas.TriageOutput)
def crear_triage(datos: schemas.TriageInput, db: Session = Depends(get_db)):
    """Registra un paciente, aplica la clasificación y guarda el resultado."""
    resultado = clasificar_triage(
        intensidad_dolor=datos.intensidad_dolor,
        fiebre=datos.fiebre,
        dificultad_respirar=datos.dificultad_respirar,
        sangrado=datos.sangrado,
        perdida_conocimiento=datos.perdida_conocimiento,
    )

    registro = models.TriageRecord(
        nombre=datos.nombre,
        edad=datos.edad,
        sintoma_principal=datos.sintoma_principal,
        descripcion=datos.descripcion,
        intensidad_dolor=datos.intensidad_dolor,
        fiebre=datos.fiebre,
        dificultad_respirar=datos.dificultad_respirar,
        sangrado=datos.sangrado,
        perdida_conocimiento=datos.perdida_conocimiento,
        nivel=resultado["nivel"],
        color=resultado["color"],
        recomendacion=resultado["recomendacion"],
        explicacion=resultado["explicacion"],
    )

    db.add(registro)
    db.commit()
    db.refresh(registro)
    return registro


@app.get("/triage", response_model=List[schemas.TriageOutput])
def listar_triage(db: Session = Depends(get_db)):
    """Devuelve todos los registros de triage, del más reciente al más antiguo."""
    return db.query(models.TriageRecord).order_by(models.TriageRecord.id.desc()).all()


@app.get("/estadisticas", response_model=schemas.Estadisticas)
def obtener_estadisticas(db: Session = Depends(get_db)):
    """Devuelve el total de pacientes y la cantidad por nivel de urgencia."""
    total = db.query(models.TriageRecord).count()

    def contar(nivel: str) -> int:
        return (
            db.query(models.TriageRecord)
            .filter(models.TriageRecord.nivel == nivel)
            .count()
        )

    return schemas.Estadisticas(
        total=total,
        rojo=contar("Rojo"),
        naranja=contar("Naranja"),
        amarillo=contar("Amarillo"),
        verde=contar("Verde"),
    )
