import { Link, useLocation, Navigate } from "react-router-dom";
import UrgencyBadge from "../components/UrgencyBadge.jsx";
import { COLOR_NIVEL, ICONO_NIVEL } from "../utils/niveles.js";

export default function Resultado() {
  const location = useLocation();
  const registro = location.state?.registro;

  if (!registro) {
    // Si el usuario llega aquí sin datos (ej. recargó la página), lo mandamos al formulario.
    return <Navigate to="/triage" replace />;
  }

  const fecha = new Date(registro.fecha_creacion).toLocaleString("es-ES");
  const color = COLOR_NIVEL[registro.nivel] || "#64748b";

  return (
    <div className="tarjeta resultado-tarjeta">
      <h1>Resultado del triage</h1>
      <p className="resultado-paciente">Paciente: {registro.nombre}</p>

      <div className="resultado-indicador" style={{ backgroundColor: color }} aria-hidden="true">
        {ICONO_NIVEL[registro.nivel] || "•"}
      </div>

      <UrgencyBadge nivel={registro.nivel} />

      <div className="resultado-detalle">
        <div className="resultado-fila">
          <span className="etiqueta">Recomendación</span>
          <p>{registro.recomendacion}</p>
        </div>
        <div className="resultado-fila">
          <span className="etiqueta">Explicación</span>
          <p>{registro.explicacion}</p>
        </div>
        <div className="resultado-fila">
          <span className="etiqueta">Fecha y hora</span>
          <p>{fecha}</p>
        </div>
      </div>

      <div className="acciones" style={{ justifyContent: "center" }}>
        <Link to="/triage" className="btn btn-secundario">
          Realizar otro triage
        </Link>
        <Link to="/dashboard" className="btn btn-primario">
          Ver dashboard
        </Link>
      </div>

      <p className="aviso-legal">
        <span aria-hidden="true">ℹ️</span>
        Este sistema es un prototipo académico y no reemplaza la evaluación
        de un profesional de salud.
      </p>
    </div>
  );
}
