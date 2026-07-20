/**
 * Colores e íconos de los niveles de urgencia usados solo en el frontend
 * (visual). El backend sigue siendo la fuente de verdad para el nivel
 * ("Rojo" | "Naranja" | "Amarillo" | "Verde"); estos valores no afectan
 * la clasificación, solo cómo se muestra.
 */
export const COLOR_NIVEL = {
  Rojo: "#dc2626",
  Naranja: "#f97316",
  Amarillo: "#eab308",
  Verde: "#16a34a",
};

export const ICONO_NIVEL = {
  Rojo: "🚨",
  Naranja: "⚡",
  Amarillo: "🕒",
  Verde: "✅",
};

export const NIVELES = ["Rojo", "Naranja", "Amarillo", "Verde"];
