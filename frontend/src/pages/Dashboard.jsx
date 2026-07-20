import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { obtenerEstadisticas, obtenerRegistros } from "../services/api.js";
import StatCard from "../components/StatCard.jsx";
import UrgencyBadge from "../components/UrgencyBadge.jsx";
import LoadingState from "../components/LoadingState.jsx";
import EmptyState from "../components/EmptyState.jsx";
import { COLOR_NIVEL, ICONO_NIVEL, NIVELES } from "../utils/niveles.js";

export default function Dashboard() {
  const [estadisticas, setEstadisticas] = useState(null);
  const [registros, setRegistros] = useState([]);
  const [error, setError] = useState("");
  const [cargando, setCargando] = useState(true);
  const [filtro, setFiltro] = useState("Todos");

  useEffect(() => {
    async function cargarDatos() {
      try {
        const [stats, lista] = await Promise.all([
          obtenerEstadisticas(),
          obtenerRegistros(),
        ]);
        setEstadisticas(stats);
        setRegistros(lista);
      } catch (err) {
        setError(err.message || "No se pudieron cargar los datos del dashboard.");
      } finally {
        setCargando(false);
      }
    }
    cargarDatos();
  }, []);

  const registrosFiltrados = useMemo(() => {
    if (filtro === "Todos") return registros;
    return registros.filter((registro) => registro.nivel === filtro);
  }, [registros, filtro]);

  if (cargando) return <LoadingState mensaje="Cargando dashboard..." />;
  if (error) return <p className="error-general">{error}</p>;

  return (
    <div>
      <div className="dashboard-encabezado">
        <div>
          <h1>Dashboard de triage</h1>
          <p>Resumen de pacientes registrados y su nivel de urgencia.</p>
        </div>
        <Link to="/triage" className="btn btn-primario">
          Nuevo triage
        </Link>
      </div>

      <div className="tarjetas-resumen">
        <StatCard etiqueta="Total de pacientes" valor={estadisticas.total} icono="👥" />
        <StatCard
          etiqueta="Rojo"
          valor={estadisticas.rojo}
          icono={ICONO_NIVEL.Rojo}
          color={COLOR_NIVEL.Rojo}
        />
        <StatCard
          etiqueta="Naranja"
          valor={estadisticas.naranja}
          icono={ICONO_NIVEL.Naranja}
          color={COLOR_NIVEL.Naranja}
        />
        <StatCard
          etiqueta="Amarillo"
          valor={estadisticas.amarillo}
          icono={ICONO_NIVEL.Amarillo}
          color={COLOR_NIVEL.Amarillo}
        />
        <StatCard
          etiqueta="Verde"
          valor={estadisticas.verde}
          icono={ICONO_NIVEL.Verde}
          color={COLOR_NIVEL.Verde}
        />
      </div>

      <div className="filtro-nivel" role="group" aria-label="Filtrar registros por nivel">
        {["Todos", ...NIVELES].map((nivel) => (
          <button
            key={nivel}
            type="button"
            className={filtro === nivel ? "activo" : ""}
            aria-pressed={filtro === nivel}
            onClick={() => setFiltro(nivel)}
          >
            {nivel}
          </button>
        ))}
      </div>

      {registrosFiltrados.length === 0 ? (
        <EmptyState
          mensaje={
            registros.length === 0
              ? "Aún no hay pacientes registrados."
              : `No hay pacientes en el nivel "${filtro}".`
          }
        />
      ) : (
        <div className="tabla-wrapper">
          <table className="tabla-registros">
            <thead>
              <tr>
                <th>Nombre</th>
                <th>Edad</th>
                <th>Síntoma principal</th>
                <th>Nivel</th>
                <th>Recomendación</th>
                <th>Fecha</th>
              </tr>
            </thead>
            <tbody>
              {registrosFiltrados.map((registro) => (
                <tr key={registro.id}>
                  <td>{registro.nombre}</td>
                  <td>{registro.edad}</td>
                  <td>{registro.sintoma_principal}</td>
                  <td>
                    <UrgencyBadge nivel={registro.nivel} size="sm" />
                  </td>
                  <td>{registro.recomendacion}</td>
                  <td>{new Date(registro.fecha_creacion).toLocaleString("es-ES")}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
