-- Esquema de referencia de la base de datos HealthTech Triage.
-- NOTA: el backend crea esta tabla automáticamente al iniciar (SQLAlchemy).
-- Este archivo es solo para consulta/documentación o creación manual si se desea.

CREATE TABLE IF NOT EXISTS triage_records (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    edad INTEGER NOT NULL,
    sintoma_principal VARCHAR(200) NOT NULL,
    descripcion VARCHAR(1000),
    intensidad_dolor INTEGER NOT NULL,
    fiebre BOOLEAN NOT NULL DEFAULT FALSE,
    dificultad_respirar BOOLEAN NOT NULL DEFAULT FALSE,
    sangrado BOOLEAN NOT NULL DEFAULT FALSE,
    perdida_conocimiento BOOLEAN NOT NULL DEFAULT FALSE,
    nivel VARCHAR(20) NOT NULL,
    color VARCHAR(20) NOT NULL,
    recomendacion VARCHAR(300) NOT NULL,
    explicacion VARCHAR(500) NOT NULL,
    fecha_creacion TIMESTAMPTZ DEFAULT NOW()
);
