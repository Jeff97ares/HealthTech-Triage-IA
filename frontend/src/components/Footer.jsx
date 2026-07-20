export default function Footer() {
  const anio = new Date().getFullYear();

  return (
    <footer className="footer">
      <p>
        <strong>HealthTech – Plataforma de Triage Inteligente con IA</strong>
      </p>
      <p>Prototipo académico · {anio}</p>
    </footer>
  );
}
