import { Link } from "react-router-dom";

const PASOS = [
  {
    titulo: "Registrar síntomas",
    texto: "El paciente completa un formulario breve con sus síntomas principales.",
  },
  {
    titulo: "Clasificar la urgencia",
    texto: "El sistema aplica reglas clínicas simples y determina el nivel de gravedad.",
  },
  {
    titulo: "Recomendar atención",
    texto: "Se sugiere si el caso requiere atención presencial, prioritaria o virtual.",
  },
];

function IlustracionSalud() {
  return (
    <svg viewBox="0 0 320 260" role="img" aria-label="Ilustración de salud con cruz médica y línea de pulso">
      <circle cx="160" cy="130" r="115" fill="#e6f2f5" />
      <circle cx="160" cy="130" r="80" fill="#ccfbf1" />
      <rect x="130" y="70" width="60" height="120" rx="14" fill="#0f6e8c" />
      <rect x="100" y="100" width="120" height="60" rx="14" fill="#0f6e8c" />
      <rect x="140" y="82" width="40" height="96" rx="8" fill="#ffffff" />
      <rect x="112" y="110" width="96" height="40" rx="8" fill="#ffffff" />
      <polyline
        points="20,220 90,220 105,190 120,235 135,205 150,220 300,220"
        fill="none"
        stroke="#0d9488"
        strokeWidth="6"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export default function Home() {
  return (
    <div>
      <section className="hero">
        <div className="hero-texto">
          <h1>Triage inteligente para una atención médica mejor priorizada</h1>
          <p>
            Registra síntomas, clasifica automáticamente el nivel de urgencia
            y recomienda el tipo de atención adecuado, para que los centros
            médicos prioricen mejor a sus pacientes.
          </p>
          <div className="acciones">
            <Link to="/triage" className="btn btn-primario">
              Realizar triage
            </Link>
            <Link to="/dashboard" className="btn btn-secundario">
              Ver dashboard
            </Link>
          </div>
        </div>
        <div className="hero-ilustracion">
          <IlustracionSalud />
        </div>
      </section>

      <section>
        <div className="tarjeta-titulo-seccion">
          <h2>¿Cómo funciona?</h2>
          <p>Un proceso simple de tres pasos, del síntoma a la recomendación.</p>
        </div>
        <div className="pasos">
          {PASOS.map((paso, indice) => (
            <div className="paso" key={paso.titulo}>
              <span className="paso-numero">{indice + 1}</span>
              <h3>{paso.titulo}</h3>
              <p>{paso.texto}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="dos-columnas" style={{ marginTop: "1.5rem" }}>
        <div className="tarjeta">
          <h2>Problema</h2>
          <p>
            Los centros médicos tienen saturación de pacientes y dificultades
            para priorizar correctamente los casos según su gravedad.
          </p>
        </div>
        <div className="tarjeta">
          <h2>Solución</h2>
          <p>
            Un sistema web que permite ingresar síntomas, realiza un triage
            automatizado, clasifica la urgencia del paciente, recomienda
            atención virtual o presencial, y muestra los registros en un
            dashboard sencillo.
          </p>
        </div>
      </section>

      <section className="tarjeta">
        <span className="etiqueta-modelo">Modelo de negocio</span>
        <h2>Pensado para clínicas y centros médicos</h2>
        <div className="dos-columnas" style={{ marginTop: "1rem" }}>
          <div>
            <p>
              <strong>Cliente objetivo:</strong> clínicas y centros médicos.
            </p>
            <p>
              <strong>Modelo:</strong> B2B, mediante suscripción SaaS mensual.
            </p>
          </div>
          <div>
            <div className="plan">
              <h3>Plan básico</h3>
              <p>Formulario de síntomas, clasificación automática y dashboard.</p>
            </div>
            <div className="plan">
              <h3>Plan profesional</h3>
              <p>Futuras integraciones con IA avanzada y reportes detallados.</p>
            </div>
          </div>
        </div>
      </section>

      <p className="aviso-legal">
        <span aria-hidden="true">ℹ️</span>
        Este sistema es un prototipo académico y no reemplaza la evaluación
        de un profesional de salud.
      </p>
    </div>
  );
}
