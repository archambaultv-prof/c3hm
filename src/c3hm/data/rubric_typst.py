import textwrap
from pathlib import Path

from c3hm.data.rubric import Rubric


def get_colors(nb_levels: int) -> list[str]:
    if nb_levels < 1:
        raise ValueError("Le nombre de niveaux doit être au moins 1.")
    if nb_levels > 5:
        raise ValueError("Le nombre de niveaux ne peut pas dépasser 5.")

    # Couleurs de base pour les 5 niveaux
    base_colors = [
        "#C8FFC8",
        "#F0FFB0",
        "#FFF8C2",
        "#FFE4C8",
        "#FFC8C8"
    ]
    match nb_levels:
        case 1:
            return [base_colors[0]]
        case 2:
            return [base_colors[0], base_colors[3]]
        case 3:
            return [base_colors[0], base_colors[1], base_colors[3]]
        case 4:
            return [base_colors[0], base_colors[1], base_colors[2], base_colors[3]]
        case _:
            return base_colors

class TypstWriter:
    def __init__(self, rubric: Rubric):
        self.rubric = rubric

    def write_typst_file(self, output_path: Path) -> None:
        with open(output_path, "w", encoding="utf-8") as f:
            content = [self._preamble()]
            content.append(self._title())
            content.append(self._course_info())
            if self.rubric.student is not None and self.rubric.comment:
                content.append('== Commentaires de l’enseignant')
                content.append(self.rubric.comment)
            content.append(self._grid_table())
            content.append(self._warning_note())
            f.write("\n".join(content))

    def _title(self) -> str:
        if self.rubric.student is not None:
            return f"#title(\"Grille d’évaluation - {self.rubric.evaluation} - {self.rubric.student.fullname()}\")"
        return f"#title(\"Grille d’évaluation - {self.rubric.evaluation}\")"

    def _course_info(self) -> str:
        return textwrap.dedent(f"""
            / Cours: {self.rubric.course}
            / Session: {self.rubric.session}
            """)

    def _preamble(self) -> str:
        color_codes = ""
        for i, color in enumerate(get_colors(len(self.rubric.grid.levels))):
            color_codes += f'#let COLOR_{i} = rgb("{color}")\n'
        return textwrap.dedent(f"""
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

            {color_codes}

            #set table.cell(inset: (x: 0.5em, y: 0.75em)) // To go around the issue with hline and row-gutters
            #show table.cell.where(y: 0): set text(weight: "bold")
            #show table.cell: set text(size: 10pt)
            #show table.cell: set par(justify: false)
            """)

    def _grid_table(self) -> str:
        s = [self._grid_table_header()]
        s.extend(self._table_rows())
        s.extend([")", ""])
        return "\n".join(s)

    def _grid_table_header(self) -> str:
        columns = ", ".join(["1fr"] * (len(self.rubric.grid.levels) + 1))
        s = textwrap.dedent(f"""
            #table(
            columns: ({columns}),
            stroke: none,
            fill: (x, y) => if y == 0 {{
                if x == 1 {{ COLOR_0 }}
                else if x == 2 {{ COLOR_1 }}
                else if x == 3 {{ COLOR_2 }}
                else if x == 4 {{ COLOR_3 }}
                else if x == 5 {{ COLOR_4 }}
            }},
            """)
        if self.rubric.student is not None:
            s += f'table.header([Note : {self.rubric.final_grade():.0f}~/~100],'
        else:
            s += 'table.header([Critère (100~pts)],'
        if self.rubric.grid.show_levels_percentage:
            for level in self.rubric.grid.levels:
                s += f'[{level.label} ({level.percentage * 100:.0f}%)],'
        else:
            for level in self.rubric.grid.levels:
                s += f'[{level.label}],'
        s += ' table.hline(stroke: 1pt)),'
        return s

    def _warning_note(self) -> str:
        return textwrap.dedent("""
            La grille ci-dessus sert de guide pour soutenir le jugement
            professionnel de l’enseignant et n’est pas exhaustive. La note
            finale peut être ajustée en présence d’une erreur significative ou
            d’un non-respect des attentes implicites de qualité (bonnes
            pratiques, conventions, lisibilité, sécurité, etc.). Une erreur
            significative peut entraîner la révision du poids d’un critère.
            """)

    def _table_rows(self) -> list[str]:
        rows = []
        for criterion in self.rubric.grid.criteria:
            pts = ""
            if self.rubric.grid.show_criteria_points:
                if self.rubric.student is None:
                    pts = f" ({criterion.points()}~pts)"
                else:
                    grade = criterion.grade(self.rubric.grid)
                    pts = f" ({grade:.0f}~/~{criterion.points()})"
            rows.append(f'[*{criterion.label}{pts}*], {", ".join(["[]"] * (len(self.rubric.grid.levels)))},')
            for indicator in criterion.indicators:
                # Détermination de la colonne à colorer selon `niveau noté`
                highlight_idx = None
                highlight_color = None
                if indicator.graded_level is not None:
                    rank = self.rubric.grid.level_to_rank(indicator.graded_level)
                    match rank:
                        case 0:
                            highlight_idx, highlight_color = 0, "COLOR_0"
                        case 1:
                            highlight_idx, highlight_color = 1, "COLOR_1"
                        case 2:
                            highlight_idx, highlight_color = 2, "COLOR_2"
                        case 3:
                            highlight_idx, highlight_color = 3, "COLOR_3"
                        case 4:
                            highlight_idx, highlight_color = 4, "COLOR_4"

                # Construction des cellules de descripteurs, avec coloration si nécessaire
                descriptor_cells = []
                for i, desc in enumerate(indicator.descriptors):
                    if highlight_idx is not None and i == highlight_idx:
                        descriptor_cells.append(f'box(fill: {highlight_color})[{desc}]')
                    else:
                        descriptor_cells.append(f'[{desc}]')

                rows.append(f'[{indicator.label}], {", ".join(descriptor_cells)},')
        return rows
