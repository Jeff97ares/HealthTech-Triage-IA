# HealthTech – Plataforma de Triage Inteligente con IA

Proyecto académico (MVP). Aplicación web que registra los síntomas de un
paciente, clasifica el nivel de urgencia (Rojo, Naranja, Amarillo, Verde)
mediante un motor de reglas, y recomienda el tipo de atención médica.

> Este sistema es un prototipo académico y no reemplaza la evaluación de un
> profesional de salud.

## Tecnologías

- Frontend: React + Vite
- Backend: Python + FastAPI
- Base de datos: PostgreSQL
- IA: clasificación por reglas (sin dependencia de APIs externas). Existe un
  punto de extensión opcional para conectar un LLM en el futuro
  (`backend/app/llm_connector.py`), pero el sistema funciona sin él.

## 1. Requisitos necesarios

- Python 3.10 o superior
- Node.js 18 o superior
- PostgreSQL 14 o superior (servidor corriendo localmente)
- npm (incluido con Node.js)

## 2. Crear la base de datos PostgreSQL

Abre una terminal con `psql` (o usa pgAdmin) y crea la base de datos:

```sql
CREATE DATABASE healthtech_triage;
```

La tabla `triage_records` se crea automáticamente al iniciar el backend, no
es necesario ejecutar ningún script manualmente. El archivo
`database/schema.sql` se incluye solo como referencia de la estructura.

## 3. Configurar el archivo .env

**Backend**: copia `backend/.env.example` a `backend/.env` y ajusta los
valores según tu instalación de PostgreSQL:

```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/healthtech_triage
FRONTEND_URL=http://localhost:5173
OPENAI_API_KEY=
```

**Frontend**: copia `frontend/.env.example` a `frontend/.env`:

```
VITE_API_URL=http://localhost:8000
```

> Nota: si en tu máquina los puertos 8000 y/o 5173 ya están ocupados por otra
> aplicación, FastAPI y Vite tomarán el siguiente puerto libre (por ejemplo
> 8001 y 5174). En ese caso ajusta `VITE_API_URL` (frontend/.env) y
> `FRONTEND_URL` (backend/.env) para que coincidan con los puertos reales
> que muestran las terminales al iniciar cada servidor.

## 4. Instalar el backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # En Windows
# source venv/bin/activate   # En Mac/Linux
pip install -r requirements.txt
```

## 5. Ejecutar FastAPI

```bash
cd backend
uvicorn app.main:app --reload
```

La API quedará disponible en `http://localhost:8000`.
Documentación interactiva automática en `http://localhost:8000/docs`.

## 6. Instalar el frontend

En otra terminal:

```bash
cd frontend
npm install
```

## 7. Ejecutar React

```bash
cd frontend
npm run dev
```

El frontend quedará disponible en `http://localhost:5173`.

## 8. Direcciones a abrir en el navegador

- `http://localhost:5173/` — Página de inicio
- `http://localhost:5173/triage` — Formulario de síntomas
- `http://localhost:5173/dashboard` — Dashboard de registros
- `http://localhost:8000/docs` — Documentación de la API (Swagger)

## 9. Cómo probar el sistema

1. Con el backend y el frontend corriendo, abre `http://localhost:5173/`.
2. Haz clic en **Realizar triage** y completa el formulario con datos de
   prueba (por ejemplo: nombre "Juan Pérez", edad 30, síntoma "dolor de
   cabeza", intensidad de dolor 5, sin señales graves).
3. Al enviar, verás la página de resultado con el nivel de urgencia, color,
   recomendación y explicación.
4. Ve a **Ver dashboard** para confirmar que el paciente aparece en la tabla
   y que las tarjetas de resumen se actualizaron.
5. Repite el formulario variando los valores (dolor, fiebre, dificultad para
   respirar, sangrado, pérdida de conocimiento) para comprobar los cuatro
   niveles de clasificación:
   - Pérdida de conocimiento, dificultad para respirar o sangrado → **Rojo**
   - Dolor ≥ 8 → **Naranja**
   - Fiebre o dolor entre 4 y 7 → **Amarillo**
   - Dolor entre 1 y 3 sin señales graves → **Verde**

## Endpoints de la API

| Método | Ruta            | Descripción                                          |
|--------|-----------------|-------------------------------------------------------|
| GET    | `/`             | Verifica que la API está funcionando                  |
| POST   | `/triage`       | Registra un paciente y devuelve su clasificación       |
| GET    | `/triage`       | Devuelve todos los registros                           |
| GET    | `/estadisticas` | Devuelve el total de pacientes y cantidad por nivel     |

## Estructura del proyecto

```
healthtech-triage/
├── frontend/       React + Vite (páginas Home, Triage, Resultado, Dashboard)
├── backend/        FastAPI (API REST + motor de clasificación por reglas)
├── database/       schema.sql de referencia
├── README.md
├── .gitignore
└── .env.example
```

## Fuera de alcance (a propósito)

Este MVP no incluye: login, registro de usuarios, pagos, videollamadas,
geolocalización, historial clínico completo, roles de usuario, recuperación
de contraseña, notificaciones, app móvil, entrenamiento de modelos de IA,
integraciones externas ni Docker.
