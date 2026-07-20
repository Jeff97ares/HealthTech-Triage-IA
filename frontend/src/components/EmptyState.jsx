export default function EmptyState({ mensaje, icono = "📋" }) {
  return (
    <div className="estado-vacio">
      <span className="icono" aria-hidden="true">
        {icono}
      </span>
      <p>{mensaje}</p>
    </div>
  );
}
