import { useEffect, useState } from "react";
import { NavLink, useLocation } from "react-router-dom";

const enlaceClase = ({ isActive }) => (isActive ? "activo" : undefined);

export default function Navbar() {
  const [abierto, setAbierto] = useState(false);
  const location = useLocation();

  useEffect(() => {
    setAbierto(false);
  }, [location.pathname]);

  return (
    <header className="navbar">
      <NavLink to="/" className="navbar-brand">
        <span className="icono-marca" aria-hidden="true">
          🩺
        </span>
        HealthTech Triage
      </NavLink>

      <button
        type="button"
        className="navbar-toggle"
        aria-expanded={abierto}
        aria-label="Abrir menú de navegación"
        onClick={() => setAbierto((valor) => !valor)}
      >
        ☰
      </button>

      <nav className={`navbar-links ${abierto ? "abierto" : ""}`}>
        <NavLink to="/" end className={enlaceClase}>
          Inicio
        </NavLink>
        <NavLink to="/triage" className={enlaceClase}>
          Realizar triage
        </NavLink>
        <NavLink to="/dashboard" className={enlaceClase}>
          Dashboard
        </NavLink>
      </nav>
    </header>
  );
}
