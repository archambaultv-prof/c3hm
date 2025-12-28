import subprocess
import textwrap
from pathlib import Path

import yaml

from c3hm.data.rubric import DEFAULT_DESCRIPTORS, validate_rubric

PREAMBULE = textwrap.dedent("""
    #set text(
        lang: "fr",
        hyphenate: true,
    )

    #set page(
        paper: "us-letter",
        flipped: true,
        numbering: "1 / 1",
        margin: (x: 0.5in, y: 0.5in)
    )
    #set par(justify: true)

    #let PERFECT_GREEN   = rgb("#C8FFC8")
    #let VERY_GOOD_GREEN = rgb("#F0FFB0")
    #let HALF_WAY_YELLOW = rgb("#FFF8C2")
    #let MINIMAL_RED     = rgb("#FFE4C8")
    #let BAD_RED         = rgb("#FFC8C8")

    #set table.cell(inset: (x: 0.5em, y: 0.75em)) // To go around the issue with hline and row-gutters
    #show table.cell.where(y: 0): set text(weight: "bold")
    #show table.cell: set text(size: 10pt)
    """)

def rubric_table_header(grade: float | None = None) -> str:
    s = textwrap.dedent("""
        #table(
        columns: (1fr, 1fr, 1fr, 1fr, 1fr, 1fr),
        stroke: none,
        fill: (x, y) => if y == 0 {
            if x == 1 { PERFECT_GREEN }
            else if x == 2 { VERY_GOOD_GREEN }
            else if x == 3 { HALF_WAY_YELLOW }
            else if x == 4 { MINIMAL_RED }
            else if x == 5 { BAD_RED }
        },
        """)
    if grade is not None:
        s += f'table.header([Note : {grade:.0f} / 100],[Très bien (100%)],[Bien (80%)],[Passable (60%)],[À améliorer (30%)],[Insuffisant (0%)], table.hline(stroke: 1pt)),'
    else:
        s += 'table.header([Critère (100 pts)],[Très bien (100%)],[Bien (80%)],[Passable (60%)],[À améliorer (30%)],[Insuffisant (0%)], table.hline(stroke: 1pt)),'
    return s



def export_rubric(input_path: Path, output_path: Path) -> None:
    with open(input_path, encoding="utf-8") as f:
        content = f.read()
    rubric = yaml.safe_load(content)
    export_rubric_data(rubric, output_path)

def export_rubric_data(rubric_data: dict, output_path: Path) -> None:
    validate_rubric(rubric_data)

    # Préambule et en-tête
    s = [PREAMBULE, ""]
    if "nom" in rubric_data:
        matricule = f" ({rubric_data['matricule']})" if "matricule" in rubric_data else ""
        s.append(f'#title("Grille d’évaluation - {rubric_data['nom']}{matricule}")')
    else:
        s.append('#title("Grille d’évaluation")')
    s.append(f"/ Cours: {rubric_data['cours']}")
    s.append(f"/ Session: {rubric_data['session']}")
    s.append(f"/ Évaluation: {rubric_data['évaluation']}")

    # Tableau des critères
    if "nom" in rubric_data:
        s.append(rubric_table_header(rubric_data["note"]))
    else:
        s.append(rubric_table_header())
    s.extend(table_rows(rubric_data))
    s.extend([")", ""])

    # Bonus malus
    if "nom" in rubric_data:
        s.append('')
        bonus_malus = rubric_data.get("bonus malus", {})
        points = bonus_malus.get("points")
        if points is not None and points != 0:
            raison = bonus_malus.get("raison")
            points_str = f"{points} pts"
            s.append("#heading(numbering: none, level: 1)[Bonus / Malus]")
            s.append(f"/ Points: {points_str}")
            if raison is not None:
                s.append(f"/ Raison: {raison}")
            s.append("")
    else:
        s.append('')
        s.append("#heading(numbering: none, level: 1)[Bonus / Malus]")
        s.append("En plus de la grille ci-dessus, il est possible que des points de bonus ou de malus soient appliqués,"
                 " notamment pour:")
        s.append("- un retard dans la remise du travail")
        s.append("- des fautes de français")
        s.append("- une erreur significative (non respect des consignes, code spaghetti, code qui plante ou ne démarre pas, etc.)")

    # Commentaire
    if "nom" in rubric_data and rubric_data["commentaire"]:
        s.append("#heading(numbering: none, level: 1)[Commentaire]")
        s.append(rubric_data["commentaire"])
        s.append("")

    # Compilation
    output_typst = output_path.with_suffix(".typ")
    with open(output_typst, "w", encoding="utf-8") as f:
        f.write("\n".join(s))

    output_path = output_path.with_suffix(".pdf")
    compile_typst_file(output_typst, output_path)

    # Nettoyage du fichier temporaire
    output_typst.unlink()

def table_rows(data: dict) -> list[str]:
    rows = []
    for item in data["critères"]:
        if "section" in item:
            rows.append(f'[*{item["section"]}*], [], [], [], [], [],')
        elif "critère" in item:
            # Détermination de la colonne à colorer selon `percentage`
            percentage = item.get("pourcentage")
            highlight_idx = None
            highlight_color = None
            if percentage is not None:
                if percentage == 1.0:
                    highlight_idx, highlight_color = 0, "PERFECT_GREEN"      # Très bien (100%)
                elif percentage >= 0.8:
                    highlight_idx, highlight_color = 1, "VERY_GOOD_GREEN"    # Bien (80%)
                elif percentage >= 0.6:
                    highlight_idx, highlight_color = 2, "HALF_WAY_YELLOW"    # Passable (60%)
                elif percentage >= 0.3:
                    highlight_idx, highlight_color = 3, "MINIMAL_RED"        # À améliorer (30%)
                else:
                    highlight_idx, highlight_color = 4, "BAD_RED"            # Insuffisant (0%)

            # Construction des cellules de descripteurs, avec coloration si nécessaire
            descs = item.get("descripteurs", DEFAULT_DESCRIPTORS)
            descriptor_cells = []
            for i, desc in enumerate(descs):
                if highlight_idx is not None and i == highlight_idx:
                    descriptor_cells.append(f'box(fill: {highlight_color})[{desc}]')
                else:
                    descriptor_cells.append(f'[{desc}]')

            pts = f"{item['note']}~/~{item['points']}" if "note" in item else f"{item['points']}~pts"
            rows.append(f'[{item["critère"]} ({pts})], {", ".join(descriptor_cells)},')

            # Ajout d'un commentaire si présent
            if "nom" in data and "commentaire" in item and item["commentaire"] is not None and item["commentaire"].strip():
                rows.append(f'[#align(right)[_Commentaire_]], table.cell(colspan: 5)[{item["commentaire"]}],')
        else:
            raise ValueError("Chaque élément doit être une section ou un critère.")
    return rows

def compile_typst_file(input_path: Path, output_path: Path) -> None:
    result = subprocess.run(
        ["typst", "compile", str(input_path), str(output_path)],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(f"Erreur lors de la compilation du fichier Typst:\n{result.stderr}")
