# HealthTech – Plataforma de Triage Inteligente con IA

Proyecto académico. Aplicación web que registra los síntomas de un paciente,
clasifica el nivel de urgencia (Rojo, Naranja, Amarillo, Verde) y recomienda
el tipo de atención médica (emergencia, presencial o virtual).

> **HealthTech es un prototipo académico de apoyo a la priorización. No
> diagnostica enfermedades ni reemplaza la evaluación de profesionales de
> salud.**

## Arquitectura

- **Frontend**: React + Vite (React Router, 4 páginas: Inicio, Triage,
  Resultado, Dashboard).
- **Backend**: Python + FastAPI.
- **Base de datos**: PostgreSQL (tabla `triage_records`).
- **IA**: motor híbrido reglas + LLM (OpenAI, SDK oficial `openai>=1.x`).

```
React (5174)  →  FastAPI (8001)  →  Motor de reglas (siempre)
                                  →  LLM de OpenAI (opcional, si está configurado)
                                  →  Motor híbrido (combina ambos)
                                  →  PostgreSQL (5434)
```

### Motor híbrido: reglas + IA

El motor de reglas (`backend/app/triage_engine.py`) es el mecanismo de
**seguridad** y siempre se ejecuta, sin depender de ningún servicio externo.
La IA (`backend/app/services/ai_triage_service.py`) es un apoyo **opcional**:
recibe únicamente datos clínicos (edad, síntoma principal, descripción,
intensidad del dolor y las 4 señales de alarma) — **nunca el nombre del
paciente** — y devuelve una sugerencia estructurada y validada con Pydantic.

`backend/app/triage_hibrido.py` combina ambos resultados aplicando siempre
el **principio de mayor seguridad**: se usa el nivel más severo entre reglas
e IA (orden ROJO > NARANJA > AMARILLO > VERDE). La IA nunca puede reducir
una prioridad detectada por las reglas; solo puede igualarla o elevarla.

Si la IA no está habilitada, no tiene clave configurada, falla, se
agota el tiempo de espera, o responde algo que no cumple el esquema
esperado, el sistema usa **únicamente** el resultado de las reglas y el
registro se guarda con `fuente_clasificacion = "REGLAS"`. El formulario
nunca queda inutilizable por un error de la IA.

## 1. Requisitos necesarios

- Python 3.9 o superior
- Node.js 18 o superior
- PostgreSQL 14 o superior (servidor corriendo localmente)
- npm (incluido con Node.js)
- (Opcional) una clave de API de OpenAI, solo si quieres activar la
  clasificación asistida por IA

## 2. Crear la base de datos PostgreSQL

Abre una terminal con `psql` (o usa pgAdmin) y crea la base de datos:

```sql
CREATE DATABASE healthtech_triage;
```

La tabla `triage_records` se crea automáticamente al iniciar el backend, y
las columnas nuevas del motor híbrido se agregan de forma seguridad
(`ADD COLUMN IF NOT EXISTS`, sin borrar ni recrear la tabla). El archivo
`database/schema.sql` se incluye solo como referencia de la estructura base.

## 3. Crear y activar el entorno virtual del backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # En Windows
# source .venv/bin/activate   # En Mac/Linux
```

## 4. Instalar el backend

```bash
pip install -r requirements.txt
```

## 5. Configurar el archivo .env

**Backend**: copia `backend/.env.example` a `backend/.env` y ajusta los
valores según tu instalación:

```
DATABASE_URL=postgresql://postgres@127.0.0.1:5434/healthtech_triage
FRONTEND_URL=http://localhost:5174

AI_ENABLED=false
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
AI_TIMEOUT_SECONDS=8
```

**Frontend**: copia `frontend/.env.example` a `frontend/.env`:

```
VITE_API_URL=http://localhost:8001
```

> Nota: si en tu máquina los puertos por defecto (8000, 5173) ya están
> ocupados por otra aplicación, FastAPI y Vite tomarán el siguiente puerto
> libre. Ajusta `VITE_API_URL` (frontend/.env) y `FRONTEND_URL`
> (backend/.env) para que coincidan con los puertos reales que muestran las
> terminales al iniciar cada servidor.

### Cómo obtener y colocar tu clave de OpenAI (sin publicarla)

1. Crea una clave en <https://platform.openai.com/api-keys> (requiere una
   cuenta de OpenAI con facturación configurada).
2. Pégala en `backend/.env` (nunca en `backend/.env.example`, nunca en el
   código, nunca en el frontend):
   ```
   AI_ENABLED=true
   OPENAI_API_KEY=sk-tu-clave-real-aqui
   OPENAI_MODEL=gpt-4o-mini
   ```
3. `backend/.env` está en `.gitignore` (junto con cualquier `.env*`, excepto
   los `.env.example`), así que `git status` nunca debería mostrarlo. Antes
   de hacer commit, confirma que no aparezca:
   ```bash
   git status
   ```
4. La clave se lee únicamente desde variables de entorno
   (`backend/app/config.py`); nunca se imprime en logs ni se envía al
   frontend. El endpoint `GET /api/ai/status` confirma si está configurada
   sin revelarla.

### Cómo desactivar temporalmente la IA

Pon `AI_ENABLED=false` en `backend/.env` (o simplemente deja
`OPENAI_API_KEY` vacío) y reinicia el backend. El sistema seguirá
funcionando exactamente igual, usando solo el motor de reglas.

## 6. Ejecutar FastAPI

```bash
cd backend
uvicorn app.main:app --reload --port 8001
```

La API quedará disponible en `http://localhost:8001`.
Documentación interactiva automática en `http://localhost:8001/docs`.

## 7. Instalar el frontend

En otra terminal:

```bash
cd frontend
npm install
```

## 8. Ejecutar React

```bash
cd frontend
npm run dev
```

El frontend quedará disponible en `http://localhost:5174` (o el siguiente
puerto libre que indique la terminal).

## 9. Direcciones a abrir en el navegador

- `http://localhost:5174/` — Página de inicio
- `http://localhost:5174/triage` — Formulario de síntomas
- `http://localhost:5174/dashboard` — Dashboard de registros
- `http://localhost:8001/docs` — Documentación de la API (Swagger)
- `http://localhost:8001/api/ai/status` — Estado de la integración de IA

## 10. Cómo probar el sistema

1. Con el backend y el frontend corriendo, abre `http://localhost:5174/`.
2. Haz clic en **Realizar triage** y completa el formulario con datos de
   prueba (por ejemplo: nombre "Juan Pérez", edad 30, síntoma "dolor de
   cabeza", intensidad de dolor 5, sin señales graves).
3. Al enviar, verás la página de resultado con el nivel de urgencia, color,
   recomendación, explicación y — si la IA está activa y respondió — un
   bloque adicional "Clasificación asistida por IA" con el tipo de atención
   y las señales de alerta identificadas. Si la IA no respondió, verás:
   *"El resultado fue generado mediante el motor de reglas de seguridad."*
4. Ve a **Ver dashboard** para confirmar que el paciente aparece en la
   tabla (columna **Fuente**: "IA + reglas" o "Solo reglas") y que las
   tarjetas de resumen se actualizaron.
5. Repite el formulario variando los valores para comprobar los cuatro
   niveles de clasificación por reglas:
   - Pérdida de conocimiento, dificultad para respirar o sangrado → **Rojo**
   - Dolor ≥ 8 → **Naranja**
   - Fiebre o dolor entre 4 y 7 → **Amarillo**
   - Dolor entre 1 y 3 sin señales graves → **Verde**

## 11. Cómo ejecutar las pruebas

```bash
cd backend
.venv\Scripts\activate        # En Windows
pytest -v
```

Las pruebas **nunca llaman a la API real de OpenAI** (todo se simula con
mocks) y **nunca usan la base de datos real**: crean automáticamente una
base de datos aislada (`healthtech_triage_test`) antes de correr, y la
eliminan al finalizar. `healthtech_triage` no se toca en ningún momento.

Casos cubiertos: los 4 niveles del motor de reglas, que la IA nunca puede
reducir una clasificación Rojo, que la IA puede elevar la prioridad, que el
sistema funciona sin clave API / con `AI_ENABLED=false` / cuando la API
falla o responde algo inválido, que el nombre del paciente nunca se envía
al LLM, y que los registros se guardan correctamente en PostgreSQL.

## Endpoints de la API

| Método | Ruta              | Descripción                                                        |
|--------|-------------------|---------------------------------------------------------------------|
| GET    | `/`               | Verifica que la API está funcionando                                |
| POST   | `/triage`         | Registra un paciente, clasifica (reglas + IA) y guarda el resultado |
| GET    | `/triage`         | Devuelve todos los registros                                        |
| GET    | `/estadisticas`   | Devuelve el total de pacientes y cantidad por nivel                 |
| GET    | `/api/ai/status`  | Indica si la IA está habilitada/configurada (sin exponer la clave)  |

## Variables de entorno (backend/.env)

| Variable              | Requerida | Descripción                                              |
|------------------------|-----------|-----------------------------------------------------------|
| `DATABASE_URL`         | Sí        | Cadena de conexión a PostgreSQL                            |
| `FRONTEND_URL`         | Sí        | Origen permitido para CORS                                 |
| `AI_ENABLED`           | No        | `true`/`false`. Si es `false`, se usa solo el motor de reglas |
| `OPENAI_API_KEY`       | No        | Clave de OpenAI. Sin ella, la IA queda deshabilitada        |
| `OPENAI_MODEL`         | No        | Modelo a usar (por defecto `gpt-4o-mini`)                   |
| `AI_TIMEOUT_SECONDS`   | No        | Tiempo máximo de espera a la IA (por defecto `8` segundos)  |

## Estructura del proyecto

```
healthtech-triage/
├── frontend/       React + Vite (Home, Triage, Resultado, Dashboard)
├── backend/
│   ├── app/
│   │   ├── main.py               Endpoints de la API
│   │   ├── config.py             Variables de entorno de IA
│   │   ├── triage_engine.py      Motor de reglas (seguridad)
│   │   ├── triage_hibrido.py     Combina reglas + IA
│   │   └── services/
│   │       └── ai_triage_service.py   Cliente de OpenAI + validación
│   └── tests/                    Pruebas automatizadas (pytest)
├── database/       schema.sql de referencia
├── README.md
├── .gitignore
└── .env.example
```

## Seguridad y privacidad

- El nombre del paciente **nunca** se envía a la IA; solo datos clínicos.
- La clave de OpenAI se lee únicamente desde variables de entorno del
  backend; nunca se expone en el frontend ni en el código fuente.
- Los archivos `.env` reales están excluidos de Git (`.gitignore`); solo
  los `.env.example` (sin claves reales) se versionan.
- Los datos médicos completos no se imprimen en los logs del backend; solo
  mensajes técnicos genéricos (p. ej. "IA no disponible: error de conexión").
- CORS está limitado al origen del frontend configurado en `FRONTEND_URL`.
- El proyecto no usa los datos para entrenar modelos.

## Limitaciones del prototipo

- La clasificación de la IA es orientativa: siempre requiere revisión
  profesional y nunca reemplaza una evaluación médica real.
- El motor de reglas es intencionalmente simple (fines académicos) y no
  cubre todos los escenarios clínicos posibles.
- No hay autenticación, historial clínico completo ni roles de usuario
  (fuera del alcance de este MVP, ver sección siguiente).
- La calidad de la sugerencia de IA depende del modelo configurado y puede
  variar; el sistema está diseñado para nunca confiar ciegamente en ella
  (de ahí el motor híbrido con piso de seguridad en las reglas).

## Fuera de alcance (a propósito)

Este proyecto no incluye: login, registro de usuarios, pagos,
videollamadas, geolocalización, historial clínico completo, roles de
usuario, recuperación de contraseña, notificaciones, app móvil,
entrenamiento de modelos de IA propios, otras integraciones externas ni
Docker.
