import textwrap
from pathlib import Path

from c3hm.data.rubric import Indicator, Rubric


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
            return f"#title(\"Grille d’évaluation - {self.rubric.evaluation} - {self.rubric.student.name}\")"
        return f"#title(\"Grille d’évaluation - {self.rubric.evaluation}\")"

    def _course_info(self) -> str:
        return textwrap.dedent(f"""
            / Cours: {self.rubric.course}
            / Session: {self.rubric.session}
            """)

    def _preamble(self) -> str:
        return textwrap.dedent("""
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
            #show table.cell: set par(justify: false)
            """)

    def _grid_table(self) -> str:
        s = [self._grid_table_header()]
        s.extend(self._table_rows())
        s.extend([")", ""])
        return "\n".join(s)

    def _grid_table_header(self) -> str:
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
        if self.rubric.student is not None:
            s += f'table.header([Note : {self.rubric.final_grade():.0f}~/~100],'
        else:
            s += 'table.header([Critère (100~pts)],'
        if self.rubric.show_levels_percentage:
            s += '[Avancé (100%)],[Acquis (75%)],[Ça y est presque! (50%)],[En apprentissage (25%)],[Non démontré (0%)],'
        else:
            s += '[Avancé],[Acquis],[Ça y est presque!],[En apprentissage],[Non démontré],'
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
            if self.rubric.show_criteria_points:
                if self.rubric.student is None:
                    pts = f" ({criterion.points()}~pts)"
                else:
                    grade = criterion.grade()
                    pts = f" ({grade:.0f}~/~{criterion.points()})"
            rows.append(f'[*{criterion.label}{pts}*], [], [], [], [], [],')
            for indicator in criterion.indicators:
                # Détermination de la colonne à colorer selon `niveau noté`
                highlight_idx = None
                highlight_color = None
                if indicator.graded_level is not None:
                    grade = Indicator.level_to_percentage(indicator.graded_level)
                    match grade:
                        case 1:
                            highlight_idx, highlight_color = 0, "PERFECT_GREEN"      # Avancé (100%)
                        case 0.75:
                            highlight_idx, highlight_color = 1, "VERY_GOOD_GREEN"    # Acquis (75%)
                        case 0.5:
                            highlight_idx, highlight_color = 2, "HALF_WAY_YELLOW"    # Ça y est presque! (50%)
                        case 0.25:
                            highlight_idx, highlight_color = 3, "MINIMAL_RED"        # En apprentissage (25%)
                        case 0.0:
                            highlight_idx, highlight_color = 4, "BAD_RED"            # Données insuffisantes (0%)

                # Construction des cellules de descripteurs, avec coloration si nécessaire
                descriptor_cells = []
                for i, desc in enumerate(indicator.descriptors):
                    if highlight_idx is not None and i == highlight_idx:
                        descriptor_cells.append(f'box(fill: {highlight_color})[{desc}]')
                    else:
                        descriptor_cells.append(f'[{desc}]')

                rows.append(f'[{indicator.label}], {", ".join(descriptor_cells)},')
        return rows
