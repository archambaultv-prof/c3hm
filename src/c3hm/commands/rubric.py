import subprocess
import textwrap
from pathlib import Path

from tomlkit import parse

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

    #title("Grille d’évaluation")
    """)

RUBRIC_TABLE_HEADER = textwrap.dedent("""
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
  table.header([Critère (100 pts)],[Très bien (100%)],[Bien (80%)],[Passable (60%)],[À améliorer (30%)],[Insuffisant (0%)], table.hline(stroke: 1pt)),
""")

DEFAULT_DESCRIPTORS = [
    "Le travail répond parfaitement aux attentes.",
    "Le travail répond bien aux attentes avec quelques erreurs mineures.",
    "Le travail répond partiellement aux attentes mais comporte des erreurs significatives.",
    "Le travail répond faiblement aux attentes et nécessite des améliorations significatives.",
    "Le travail ne répond pas aux attentes."
]

def export_rubric(input_path: Path, output_path: Path) -> None:
    with open(input_path, encoding="utf-8") as f:
        content = f.read()
    rubric_data = parse(content)

    s = [PREAMBULE, ""]
    s.append(f"/ Cours: {rubric_data['cours']}")
    s.append(f"/ Session: {rubric_data['session']}")
    s.append(f"/ Évaluation: {rubric_data['évaluation']}")
    s.append(RUBRIC_TABLE_HEADER)
    s.extend(table_rows(rubric_data))
    s.extend([")", ""])

    output_typst = output_path.with_suffix(".typ")
    with open(output_typst, "w", encoding="utf-8") as f:
        f.write("\n".join(s))

    output_path = output_path.with_suffix(".pdf")
    compile_typst_file(output_typst, output_path)

def table_rows(data: dict) -> list[str]:
    rows = []
    for item in data["critères"]:
        if "section" in item:
            rows.append(f'[*{item["section"]}*], [], [], [], [], [],')
        elif "critère" in item:
            descriptions = [f'[{desc}]' for desc in item.get("descripteurs", DEFAULT_DESCRIPTORS)]
            rows.append(f'[{item["critère"]} ({item["points"]} pts)], {", ".join(descriptions)},')
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
