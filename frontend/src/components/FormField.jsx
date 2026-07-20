export default function FormField({ label, htmlFor, error, hint, children }) {
  return (
    <div className="campo">
      <label htmlFor={htmlFor}>{label}</label>
      {children}
      {hint && !error && <span className="campo-ayuda">{hint}</span>}
      {error && (
        <span className="error-campo" role="alert">
          {error}
        </span>
      )}
    </div>
  );
}
