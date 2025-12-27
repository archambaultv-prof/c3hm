import textwrap
from datetime import date
from pathlib import Path


def export_template(output_path: Path) -> None:
    """
    Génère une grille d'évaluation sous format Excel.
    """
    s = textwrap.dedent(f"""
        cours = ""
        session = "{get_current_semester()}"
        "évaluation" = ""
        """)
    s += "\n"
    s += textwrap.dedent("""
        "critères" = [
            { section = "Section 1" },
            { "critère" = "Critère 1", points = 20 },
            { "critère" = "Critère 2", points = 20 },
            { section = "Section 2" },
            { "critère" = "Critère 3", points = 20 },
            { "critère" = "Critère 4", points = 20 },
            { "critère" = "Critère 5", points = 20 }
        ]
        """)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(s)

def get_current_semester() -> str:
    """
    Retourne le semestre actuel
    """
    today = date.today()
    year = today.year
    if today.month <= 5:
        return f"Hiver {year}"
    elif today.month <= 7:
        return f"Été {year}"
    else:
        return f"Automne {year}"
