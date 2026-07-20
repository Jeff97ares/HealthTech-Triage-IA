"""Pruebas del motor de reglas (sin IA). Casos 1 a 5 del checklist."""
from app.triage_engine import clasificar_triage


def test_rojo_por_dificultad_respirar():
    resultado = clasificar_triage(
        intensidad_dolor=2,
        fiebre=False,
        dificultad_respirar=True,
        sangrado=False,
        perdida_conocimiento=False,
    )
    assert resultado["nivel"] == "Rojo"


def test_rojo_por_perdida_de_conocimiento():
    resultado = clasificar_triage(
        intensidad_dolor=1,
        fiebre=False,
        dificultad_respirar=False,
        sangrado=False,
        perdida_conocimiento=True,
    )
    assert resultado["nivel"] == "Rojo"


def test_naranja_por_dolor_intenso():
    resultado = clasificar_triage(
        intensidad_dolor=8,
        fiebre=False,
        dificultad_respirar=False,
        sangrado=False,
        perdida_conocimiento=False,
    )
    assert resultado["nivel"] == "Naranja"


def test_amarillo_por_fiebre_o_dolor_moderado():
    resultado_por_fiebre = clasificar_triage(
        intensidad_dolor=2,
        fiebre=True,
        dificultad_respirar=False,
        sangrado=False,
        perdida_conocimiento=False,
    )
    resultado_por_dolor = clasificar_triage(
        intensidad_dolor=5,
        fiebre=False,
        dificultad_respirar=False,
        sangrado=False,
        perdida_conocimiento=False,
    )
    assert resultado_por_fiebre["nivel"] == "Amarillo"
    assert resultado_por_dolor["nivel"] == "Amarillo"


def test_verde_sin_senales_de_alarma():
    resultado = clasificar_triage(
        intensidad_dolor=2,
        fiebre=False,
        dificultad_respirar=False,
        sangrado=False,
        perdida_conocimiento=False,
    )
    assert resultado["nivel"] == "Verde"
