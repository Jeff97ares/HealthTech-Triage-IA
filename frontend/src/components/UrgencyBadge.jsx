import { COLOR_NIVEL, ICONO_NIVEL } from "../utils/niveles.js";

/**
 * Etiqueta de nivel de urgencia. No depende solo del color: siempre
 * incluye el ícono y el texto del nivel.
 */
export default function UrgencyBadge({ nivel, size = "md" }) {
  const color = COLOR_NIVEL[nivel] || "#64748b";
  const icono = ICONO_NIVEL[nivel] || "•";
  const clase = size === "sm" ? "etiqueta-nivel" : "badge-nivel";

  return (
    <span className={clase} style={{ backgroundColor: color }}>
      <span aria-hidden="true">{icono}</span>
      {nivel}
    </span>
  );
}
