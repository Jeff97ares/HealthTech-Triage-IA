"""Configuración común de pruebas.

Las pruebas NUNCA usan la base de datos real (healthtech_triage): se crea
una base de datos de prueba aislada (healthtech_triage_test) antes de
importar la aplicación, y se elimina al finalizar. Esto garantiza que no
se borre ni se modifique ningún registro existente.
"""
import os
import re
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from dotenv import load_dotenv

load_dotenv(BACKEND_DIR / ".env")

import psycopg2
import pytest
from fastapi.testclient import TestClient

_DATABASE_URL_ORIGINAL = os.getenv(
    "DATABASE_URL", "postgresql://postgres@127.0.0.1:5434/healthtech_triage"
)

_match = re.match(r"^(postgresql://[^/]+)/([^?]+)", _DATABASE_URL_ORIGINAL)
if not _match:
    raise RuntimeError("DATABASE_URL con formato inesperado; no se pueden ejecutar las pruebas.")

_PREFIJO_CONEXION, _NOMBRE_BD_ORIGINAL = _match.groups()
_NOMBRE_BD_PRUEBA = f"{_NOMBRE_BD_ORIGINAL}_test"
_DSN_ADMIN = f"{_PREFIJO_CONEXION}/postgres"
_DATABASE_URL_PRUEBA = f"{_PREFIJO_CONEXION}/{_NOMBRE_BD_PRUEBA}"


def _terminar_conexiones_y_dropear():
    conexion = psycopg2.connect(_DSN_ADMIN)
    conexion.autocommit = True
    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                "WHERE datname = %s AND pid <> pg_backend_pid();",
                (_NOMBRE_BD_PRUEBA,),
            )
            cursor.execute(f'DROP DATABASE IF EXISTS "{_NOMBRE_BD_PRUEBA}"')
    finally:
        conexion.close()


def _crear_base_de_datos_prueba():
    """Recrea limpia la base de datos de prueba. Nunca toca la real."""
    _terminar_conexiones_y_dropear()
    conexion = psycopg2.connect(_DSN_ADMIN)
    conexion.autocommit = True
    try:
        with conexion.cursor() as cursor:
            cursor.execute(f'CREATE DATABASE "{_NOMBRE_BD_PRUEBA}"')
    finally:
        conexion.close()


# Se ejecuta al importar conftest.py, ANTES de que los módulos de prueba
# importen app.main/app.database, para que usen la base de datos de prueba.
_crear_base_de_datos_prueba()
os.environ["DATABASE_URL"] = _DATABASE_URL_PRUEBA
os.environ.setdefault("AI_ENABLED", "false")
os.environ.setdefault("OPENAI_API_KEY", "")
os.environ.setdefault("FRONTEND_URL", "http://localhost:5174")


@pytest.fixture(scope="session")
def app_module():
    from app import main

    return main


@pytest.fixture()
def client(app_module):
    return TestClient(app_module.app)


def pytest_sessionfinish(session, exitstatus):
    """Limpieza final: cierra conexiones y elimina la base de datos de
    prueba. La base de datos real (healthtech_triage) nunca se toca."""
    try:
        from app.database import engine

        engine.dispose()
    except Exception:
        pass
    try:
        _terminar_conexiones_y_dropear()
    except Exception:
        pass
