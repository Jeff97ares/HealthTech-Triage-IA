export default function StatCard({ etiqueta, valor, icono, color }) {
  return (
    <div
      className="tarjeta-resumen"
      style={color ? { borderLeftColor: color } : undefined}
    >
      <div className="cabecera-resumen">
        <span className="icono" aria-hidden="true">
          {icono}
        </span>
      </div>
      <div className="numero" style={color ? { color } : undefined}>
        {valor}
      </div>
      <div className="etiqueta">{etiqueta}</div>
    </div>
  );
}
