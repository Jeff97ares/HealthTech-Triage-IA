export default function LoadingState({ mensaje = "Cargando..." }) {
  return (
    <div className="estado-carga" role="status" aria-live="polite">
      <span className="spinner" aria-hidden="true"></span>
      <span>{mensaje}</span>
    </div>
  );
}
