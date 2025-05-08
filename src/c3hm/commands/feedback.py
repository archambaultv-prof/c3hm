from decimal import Decimal
from pathlib import Path

import docx
import docx.enum.text
from docx.document import Document
from docx.enum.text import WD_COLOR_INDEX
from docx.table import Table
from openpyxl import Workbook
from openpyxl.cell.cell import Cell
from openpyxl.worksheet.worksheet import Worksheet

from c3hm.commands.statement import generate_rubric, set_as_table_header, set_row_borders, set_scale
from c3hm.data.config import Config
from c3hm.data.gradedrubric import GradedCriterion, GradedIndicator, GradedRubric
from c3hm.utils import round_to_nearest_quantum


def graded_rubrics_from_wb(
    wb: Workbook,
    config: Config,
) -> list[GradedRubric]:
    """
    Lit le fichier Excel et retourne une liste de GradedRubric.
    """
    graded_rubrics = []

    for ws in wb.worksheets:
        # Test si on a un nom de cellule "cthm_omnivox" dans la feuille
        cell = find_named_cell(ws, "cthm_omnivox")
        if cell is None:
            continue
        gr = graded_rubric_from_ws(ws, config)
        graded_rubrics.append(gr)

    return graded_rubrics


def find_named_cell(ws: Worksheet, named_cell: str) -> Cell | None:
    """
    Trouve une cellule nommée dans une feuille de calcul.
    Retourne la cellule si elle existe, sinon None.
    """
    # Vérifie si la cellule nommée existe
    if named_cell in ws.defined_names:
        defn = ws.defined_names[named_cell]
    else:
        return None

    for title, coord in defn.destinations:
        if title == ws.title:
            cell = ws[coord]
            return cell

    return None


def graded_rubric_from_ws(ws: Worksheet, config: Config) -> GradedRubric:
    """
    Lit une feuille de calcul et retourne un GradedRubric.
    Se fit aux noms de cellules définis dans la feuille de calcul.
    """
    rubric = config.rubric

    # Récupère le code omnivox
    cell = find_named_cell(ws, "cthm_omnivox")
    if cell is None:
        raise ValueError("La cellule nommée 'cthm_omnivox' n'existe pas dans la feuille.")
    omnivox_code = cell.value

    student = config.find_student(omnivox_code)
    if student is None:
        raise ValueError(f"L'étudiant avec le code omnivox '{omnivox_code}'"
                         " n'existe pas dans la configuration.")

    # Récupère les notes et commentaires
    graded_criteria = []
    for criterion in rubric.criteria:
        grade_cell = find_named_cell(ws, criterion.xl_grade_cell_id())
        if grade_cell is None:
            raise ValueError(f"La cellule nommée '{criterion.xl_grade_cell_id()}'"
                             " n'existe pas dans la feuille.")
        grade = round_to_nearest_quantum(Decimal(str(grade_cell.value)), rubric.pts_precision)

        # Récupère les commentaires
        comment_cell = find_named_cell(ws, criterion.xl_comment_cell_id())
        if comment_cell is None:
            raise ValueError(f"La cellule nommée '{criterion.xl_comment_cell_id()}'"
                             " n'existe pas dans la feuille.")
        comment = "" if comment_cell.value is None else str(comment_cell.value).strip()

        graded_indicators = []
        for indicator in criterion.indicators:
            # Récupère la note de l'indicateur
            ind_grade_cell = find_named_cell(ws, indicator.xl_grade_cell_id())
            if ind_grade_cell is None:
                raise ValueError(f"La cellule nommée '{indicator.xl_grade_cell_id()}'"
                                 " n'existe pas dans la feuille.")
            ind_grade = round_to_nearest_quantum(Decimal(str(ind_grade_cell.value)),
                                                 rubric.scale.precision)

            # Récupère le commentaire de l'indicateur
            ind_comment_cell = find_named_cell(ws, indicator.xl_comment_cell_id())
            if ind_comment_cell is None:
                raise ValueError(f"La cellule nommée '{indicator.xl_comment_cell_id()}'"
                                 " n'existe pas dans la feuille.")
            ind_comment = (""  if ind_comment_cell.value is None
                           else str(ind_comment_cell.value).strip())

            graded_indicator = GradedIndicator.from_indicator(
                indicator=indicator,
                grade=ind_grade,
                comment=ind_comment,
            )
            graded_indicators.append(graded_indicator)

        graded_criterion = GradedCriterion.from_criterion(
            criterion=criterion,
            graded_indicators=graded_indicators,
            grade=grade,
            comment=comment,
        )

        graded_criteria.append(graded_criterion)

    return GradedRubric.from_rubric(
        rubric=rubric,
        graded_criteria=graded_criteria,
        student=student)


def generate_feedback_rubric(graded_rubric: GradedRubric,
                             output_path: Path | str,
                             *,
                             title: str = "Grille d'évaluation") -> None:
    """
    Génère un fichier de rétroaction à partir d'une GradedRubric.
    """
    generate_rubric(graded_rubric,
                    output_path,
                    title=title,
                    set_first_row=feedback_set_first_row,
                    add_criterion=feedback_add_criterion,
                    add_comments=feedback_add_comments)


def feedback_set_first_row(rubric: GradedRubric, table: Table):
    """
    Remplit la première ligne du tableau avec le barème et les seuils.
    """

    # En-tête de la table
    set_as_table_header(table.rows[0])
    set_row_borders(table.rows[0])

    # Première cellule : Total sur X pts
    total = sum(criterion.grade for criterion in rubric.criteria)
    hdr_cells = table.rows[0].cells
    total_cell = hdr_cells[0]
    p = total_cell.paragraphs[0]
    p.text = f"Note : {total} / {rubric.total}"
    p.style = "Heading 3"

    # Barème et seuils
    set_scale(rubric, hdr_cells)


def feedback_add_criterion(table: Table,
                           criterion: GradedCriterion,
                           graded_rubric: GradedRubric):
    """
    Ajoute un critère et ses indicateurs à la table.
    """
    row = table.add_row()
    # Critère
    p = row.cells[0].paragraphs[0]
    pts = "pt" if criterion.total == 1 else "pts"
    p.text = f"{criterion.name} ({criterion.total} {pts})"
    p.style = "Heading 3"
    perfect = graded_rubric.scale[0].threshold
    score = perfect * criterion.grade / criterion.total
    for i, scale in enumerate(graded_rubric.scale):
        if score >= scale.threshold:
            p = row.cells[i + 1].paragraphs[0]
            p.text = f"{criterion.grade} / {criterion.total}"
            p.style = "Heading 3"
            break

    # Indicateurs
    for indicator in criterion.indicators:
        row = table.add_row()
        p = row.cells[0].paragraphs[0]
        run = p.add_run(indicator.name)
        run.style = "Emphasis"

        # Descripteurs alignés avec les niveaux de barème
        find_highlight = True
        for scale, descriptor in enumerate(indicator.descriptors):
            cell = row.cells[scale + 1]
            cell.text = descriptor
            if find_highlight and indicator.grade >= graded_rubric.scale[scale].threshold:
                find_highlight = False
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.font.highlight_color = WD_COLOR_INDEX.YELLOW

def feedback_add_comments(doc: Document,
                          graded_rubric: GradedRubric):
        """
        Ajoute les commentaires de l'évaluateur à la fin du document.
        """
        heading = doc.add_heading("Commentaires", level=1)
        heading.alignment = docx.enum.text.WD_PARAGRAPH_ALIGNMENT.LEFT
        for criterion in graded_rubric.criteria:
            if criterion.has_comments():
                heading = doc.add_heading(criterion.name, level=3)
                heading.alignment = docx.enum.text.WD_PARAGRAPH_ALIGNMENT.LEFT

                if criterion.comment.strip():
                    doc.add_paragraph(criterion.comment.strip())
            for indicator in criterion.indicators:
                if indicator.comment.strip():
                    p = doc.add_paragraph(f"{indicator.name} : ")
                    run = p.runs[0]
                    run.style = "Emphasis"
                    p.add_run(indicator.comment.strip())
