import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { registrarTriage } from "../services/api.js";
import FormField from "../components/FormField.jsx";

const VALORES_INICIALES = {
  nombre: "",
  edad: "",
  sintoma_principal: "",
  descripcion: "",
  intensidad_dolor: "",
  fiebre: false,
  dificultad_respirar: false,
  sangrado: false,
  perdida_conocimiento: false,
};

const SINTOMAS_GRAVES = [
  { campo: "fiebre", icono: "🌡️", etiqueta: "¿Tiene fiebre?" },
  { campo: "dificultad_respirar", icono: "🫁", etiqueta: "¿Tiene dificultad para respirar?" },
  { campo: "sangrado", icono: "🩸", etiqueta: "¿Tiene sangrado?" },
  { campo: "perdida_conocimiento", icono: "😵", etiqueta: "¿Perdió el conocimiento?" },
];

function validar(datos) {
  const errores = {};

  if (!datos.nombre.trim() || datos.nombre.trim().length < 2) {
    errores.nombre = "Ingresa el nombre del paciente (mínimo 2 caracteres).";
  }

  const edad = Number(datos.edad);
  if (datos.edad === "" || Number.isNaN(edad) || edad < 0 || edad > 120) {
    errores.edad = "Ingresa una edad válida (0 a 120).";
  }

  if (!datos.sintoma_principal.trim()) {
    errores.sintoma_principal = "Indica el síntoma principal.";
  }

  const dolor = Number(datos.intensidad_dolor);
  if (
    datos.intensidad_dolor === "" ||
    Number.isNaN(dolor) ||
    dolor < 1 ||
    dolor > 10
  ) {
    errores.intensidad_dolor = "Selecciona la intensidad del dolor (1 a 10).";
  }

  return errores;
}

export default function Triage() {
  const [datos, setDatos] = useState(VALORES_INICIALES);
  const [errores, setErrores] = useState({});
  const [errorGeneral, setErrorGeneral] = useState("");
  const [enviando, setEnviando] = useState(false);
  const navigate = useNavigate();

  function actualizarCampo(campo, valor) {
    setDatos((anterior) => ({ ...anterior, [campo]: valor }));
  }

  async function manejarEnvio(evento) {
    evento.preventDefault();
    setErrorGeneral("");

    const erroresValidacion = validar(datos);
    setErrores(erroresValidacion);
    if (Object.keys(erroresValidacion).length > 0) return;

    setEnviando(true);
    try {
      const registro = await registrarTriage({
        nombre: datos.nombre.trim(),
        edad: Number(datos.edad),
        sintoma_principal: datos.sintoma_principal.trim(),
        descripcion: datos.descripcion.trim(),
        intensidad_dolor: Number(datos.intensidad_dolor),
        fiebre: datos.fiebre,
        dificultad_respirar: datos.dificultad_respirar,
        sangrado: datos.sangrado,
        perdida_conocimiento: datos.perdida_conocimiento,
      });
      navigate("/resultado", { state: { registro } });
    } catch (error) {
      setErrorGeneral(error.message || "Ocurrió un error al registrar el triage.");
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div className="tarjeta formulario-tarjeta">
      <div className="formulario-encabezado">
        <h1>Formulario de síntomas</h1>
        <p>Completa los datos del paciente para clasificar el nivel de urgencia.</p>
      </div>

      {errorGeneral && (
        <p className="error-general" role="alert">
          {errorGeneral}
        </p>
      )}

      <form className="formulario" onSubmit={manejarEnvio} noValidate>
        <div className="fila-campos">
          <FormField label="Nombre del paciente" htmlFor="nombre" error={errores.nombre}>
            <input
              id="nombre"
              type="text"
              value={datos.nombre}
              aria-invalid={Boolean(errores.nombre)}
              onChange={(e) => actualizarCampo("nombre", e.target.value)}
            />
          </FormField>

          <FormField label="Edad" htmlFor="edad" error={errores.edad}>
            <input
              id="edad"
              type="number"
              min="0"
              max="120"
              value={datos.edad}
              aria-invalid={Boolean(errores.edad)}
              onChange={(e) => actualizarCampo("edad", e.target.value)}
            />
          </FormField>
        </div>

        <FormField
          label="Síntoma principal"
          htmlFor="sintoma_principal"
          error={errores.sintoma_principal}
        >
          <input
            id="sintoma_principal"
            type="text"
            value={datos.sintoma_principal}
            aria-invalid={Boolean(errores.sintoma_principal)}
            onChange={(e) => actualizarCampo("sintoma_principal", e.target.value)}
          />
        </FormField>

        <FormField label="Descripción breve" htmlFor="descripcion">
          <textarea
            id="descripcion"
            rows="3"
            value={datos.descripcion}
            onChange={(e) => actualizarCampo("descripcion", e.target.value)}
          />
        </FormField>

        <FormField
          label="Intensidad del dolor (1 a 10)"
          htmlFor="dolor-1"
          error={errores.intensidad_dolor}
        >
          <div
            className="escala-dolor"
            role="radiogroup"
            aria-label="Intensidad del dolor de 1 a 10"
          >
            {Array.from({ length: 10 }, (_, i) => i + 1).map((valor) => (
              <button
                key={valor}
                id={`dolor-${valor}`}
                type="button"
                role="radio"
                aria-checked={Number(datos.intensidad_dolor) === valor}
                className={Number(datos.intensidad_dolor) === valor ? "seleccionado" : ""}
                onClick={() => actualizarCampo("intensidad_dolor", valor)}
              >
                {valor}
              </button>
            ))}
          </div>
          <div className="escala-dolor-leyenda">
            <span>Leve</span>
            <span>Insoportable</span>
          </div>
        </FormField>

        <FormField label="Señales de alarma">
          <div className="grupo-sintomas">
            {SINTOMAS_GRAVES.map(({ campo, icono, etiqueta }) => (
              <label
                key={campo}
                htmlFor={campo}
                className={`sintoma-card ${datos[campo] ? "activo" : ""}`}
              >
                <input
                  id={campo}
                  type="checkbox"
                  checked={datos[campo]}
                  onChange={(e) => actualizarCampo(campo, e.target.checked)}
                />
                <span className="sintoma-icono" aria-hidden="true">
                  {icono}
                </span>
                <span className="sintoma-texto">{etiqueta}</span>
              </label>
            ))}
          </div>
        </FormField>

        <button className="btn btn-primario btn-bloque" type="submit" disabled={enviando}>
          {enviando ? (
            <>
              <span className="spinner" aria-hidden="true"></span>
              Clasificando...
            </>
          ) : (
            "Clasificar paciente"
          )}
        </button>
      </form>

      <p className="aviso-legal">
        <span aria-hidden="true">ℹ️</span>
        Este sistema es un prototipo académico y no reemplaza la evaluación
        de un profesional de salud.
      </p>
    </div>
  );
}
