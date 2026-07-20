const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function registrarTriage(datos) {
  const respuesta = await fetch(`${API_URL}/triage`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(datos),
  });
  if (!respuesta.ok) {
    const error = await respuesta.json().catch(() => ({}));
    throw new Error(error.detail ? JSON.stringify(error.detail) : "No se pudo registrar el triage.");
  }
  return respuesta.json();
}

export async function obtenerRegistros() {
  const respuesta = await fetch(`${API_URL}/triage`);
  if (!respuesta.ok) throw new Error("No se pudieron obtener los registros.");
  return respuesta.json();
}

export async function obtenerEstadisticas() {
  const respuesta = await fetch(`${API_URL}/estadisticas`);
  if (!respuesta.ok) throw new Error("No se pudieron obtener las estadísticas.");
  return respuesta.json();
}
