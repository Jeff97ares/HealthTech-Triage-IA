"""Configuración de la conexión a PostgreSQL con SQLAlchemy."""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/healthtech_triage",
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependencia de FastAPI: entrega una sesión de BD y la cierra al terminar."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Columnas nuevas para la clasificación asistida por IA. Se agregan con
# ADD COLUMN IF NOT EXISTS: no borran ni recrean la tabla, así que los
# registros existentes se conservan intactos.
_COLUMNAS_IA = [
    "ADD COLUMN IF NOT EXISTS clasificacion_reglas VARCHAR(20)",
    "ADD COLUMN IF NOT EXISTS clasificacion_ia VARCHAR(20)",
    "ADD COLUMN IF NOT EXISTS fuente_clasificacion VARCHAR(20) NOT NULL DEFAULT 'REGLAS'",
    "ADD COLUMN IF NOT EXISTS explicacion_ia VARCHAR(800)",
    "ADD COLUMN IF NOT EXISTS tipo_atencion VARCHAR(20)",
    "ADD COLUMN IF NOT EXISTS senales_alerta VARCHAR(1000)",
    "ADD COLUMN IF NOT EXISTS confianza_ia FLOAT",
]


def migrar_columnas_ia():
    """Agrega las columnas opcionales de IA a triage_records si no existen aún."""
    with engine.begin() as conexion:
        for clausula in _COLUMNAS_IA:
            conexion.execute(text(f"ALTER TABLE triage_records {clausula}"))
