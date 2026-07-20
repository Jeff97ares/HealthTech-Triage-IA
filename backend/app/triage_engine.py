"""Motor de clasificación de triage basado en reglas simples (sin IA externa)."""

AVISO_LEGAL = (
    "Este sistema es un prototipo académico y no reemplaza la evaluación "
    "de un profesional de salud."
)


def clasificar_triage(
    intensidad_dolor: int,
    fiebre: bool,
    dificultad_respirar: bool,
    sangrado: bool,
    perdida_conocimiento: bool,
) -> dict:
    """Aplica las reglas de triage en orden y devuelve nivel, color,
    recomendación y explicación.
    """

    # 1. Señales de emergencia -> Rojo
    if perdida_conocimiento or dificultad_respirar or sangrado:
        return {
            "nivel": "Rojo",
            "color": "#e53935",
            "recomendacion": "Acudir inmediatamente a emergencias.",
            "explicacion": (
                "Se detectaron señales graves (pérdida de conocimiento, "
                "dificultad para respirar o sangrado)."
            ),
        }

    # 2. Dolor muy alto -> Naranja
    if intensidad_dolor >= 8:
        return {
            "nivel": "Naranja",
            "color": "#fb8c00",
            "recomendacion": "Recibir atención presencial prioritaria.",
            "explicacion": f"El paciente reporta un dolor intenso ({intensidad_dolor}/10).",
        }

    # 3. Fiebre o dolor moderado -> Amarillo
    if fiebre or (4 <= intensidad_dolor <= 7):
        return {
            "nivel": "Amarillo",
            "color": "#fdd835",
            "recomendacion": "Programar una consulta presencial.",
            "explicacion": "El paciente presenta fiebre y/o dolor moderado.",
        }

    # 4. Dolor leve sin señales graves -> Verde
    if 1 <= intensidad_dolor <= 3:
        return {
            "nivel": "Verde",
            "color": "#43a047",
            "recomendacion": "Puede recibir consulta virtual o seguimiento en casa.",
            "explicacion": "El paciente presenta síntomas leves y sin señales de alarma.",
        }

    # Caso residual (no debería ocurrir con dolor validado entre 1 y 10)
    return {
        "nivel": "Amarillo",
        "color": "#fdd835",
        "recomendacion": "Programar una consulta presencial.",
        "explicacion": "No fue posible determinar con certeza la gravedad; se recomienda evaluación presencial.",
    }


# Color y recomendación estándar por nivel. Se usa únicamente cuando el
# motor híbrido (triage_hibrido.py) necesita re-etiquetar un nivel que la
# IA elevó por encima del resultado de clasificar_triage(); no reemplaza
# ni modifica la lógica de reglas de arriba.
NIVELES_INFO = {
    "Rojo": {
        "color": "#e53935",
        "recomendacion": "Acudir inmediatamente a emergencias.",
    },
    "Naranja": {
        "color": "#fb8c00",
        "recomendacion": "Recibir atención presencial prioritaria.",
    },
    "Amarillo": {
        "color": "#fdd835",
        "recomendacion": "Programar una consulta presencial.",
    },
    "Verde": {
        "color": "#43a047",
        "recomendacion": "Puede recibir consulta virtual o seguimiento en casa.",
    },
}


def detalle_por_nivel(nivel: str) -> dict:
    """Devuelve color y recomendación estándar para un nivel (Rojo/Naranja/
    Amarillo/Verde). Usado solo para construir el resultado final del motor
    híbrido cuando la IA escala la prioridad del resultado de reglas.
    """
    return NIVELES_INFO.get(nivel, NIVELES_INFO["Amarillo"])
