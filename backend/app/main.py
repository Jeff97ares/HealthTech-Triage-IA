"""API REST de HealthTech - Plataforma de Triage Inteligente con IA."""
import json
import logging
import os
from typing import List

from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import config, models, schemas
from .database import Base, engine, get_db, migrar_columnas_ia
from .triage_engine import clasificar_triage
from .triage_hibrido import clasificar_triage_hibrido
from .services.ai_triage_service import analizar_con_ia

load_dotenv()

logger = logging.getLogger("healthtech.main")

# Crea la tabla triage_records automáticamente al iniciar el backend
Base.metadata.create_all(bind=engine)
# Agrega las columnas opcionales de IA si aún no existen (no borra datos)
migrar_columnas_ia()

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


@app.get("/api/ai/status", response_model=schemas.EstadoIA)
def estado_ia():
    """Indica si la clasificación asistida por IA está disponible (sin
    exponer la clave API)."""
    return schemas.EstadoIA(
        ai_enabled=config.AI_ENABLED,
        provider=config.proveedor_activo_label(),
        configured=config.ai_configurada(),
    )


@app.post("/triage", response_model=schemas.TriageOutput)
def crear_triage(datos: schemas.TriageInput, db: Session = Depends(get_db)):
    """Registra un paciente, aplica la clasificación (reglas + IA cuando
    está disponible) y guarda el resultado. El motor de reglas siempre se
    ejecuta y actúa como piso de seguridad."""
    resultado_reglas = clasificar_triage(
        intensidad_dolor=datos.intensidad_dolor,
        fiebre=datos.fiebre,
        dificultad_respirar=datos.dificultad_respirar,
        sangrado=datos.sangrado,
        perdida_conocimiento=datos.perdida_conocimiento,
    )

    # La IA es un apoyo opcional: cualquier error aquí no debe impedir
    # registrar el triage con el resultado de reglas.
    resultado_ia = None
    try:
        resultado_ia = analizar_con_ia(
            {
                "edad": datos.edad,
                "sintoma_principal": datos.sintoma_principal,
                "descripcion": datos.descripcion,
                "intensidad_dolor": datos.intensidad_dolor,
                "fiebre": datos.fiebre,
                "dificultad_respirar": datos.dificultad_respirar,
                "sangrado": datos.sangrado,
                "perdida_conocimiento": datos.perdida_conocimiento,
            }
        )
    except Exception:
        logger.warning("IA no disponible: error inesperado antes de clasificar.")
        resultado_ia = None

    resultado = clasificar_triage_hibrido(resultado_reglas, resultado_ia)

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
        clasificacion_reglas=resultado["clasificacion_reglas"],
        clasificacion_ia=resultado["clasificacion_ia"],
        fuente_clasificacion=resultado["fuente_clasificacion"],
        explicacion_ia=resultado["explicacion_ia"],
        tipo_atencion=resultado["tipo_atencion"],
        senales_alerta=json.dumps(resultado["senales_alerta"], ensure_ascii=False),
        confianza_ia=resultado["confianza_ia"],
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
