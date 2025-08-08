from openpyxl import Workbook
from openpyxl.worksheet.worksheet import Worksheet

from c3hm.data.config.config import Config
from c3hm.data.config.criterion import Criterion
from c3hm.data.config.evaluation import Evaluation
from c3hm.data.config.indicator import Indicator
from c3hm.data.gradesheet.gradesheet import GradeSheet
from c3hm.data.student.students import Students
from c3hm.utils.excel import (
    CTHM_OMNIVOX,
    comment_cell_name,
    find_named_cell,
    find_worksheet,
    grade_cell_name,
)


def grades_from_wb(
    wb: Workbook,
    config: Config,
    students: Students
) -> list[GradeSheet]:
    """
    Lit le fichier Excel et retourne une liste d'évaluations notées
    """
    grade_sheets = []

    for student in students:
        ws = find_worksheet(wb, student.alias)
        grade_sheets.append(grades_from_ws(ws, config.evaluation))
    return grade_sheets


def grades_from_ws(ws: Worksheet,
                   eval: Evaluation) -> GradeSheet:
    """
    Lit une feuille de calcul et retourne une évaluation notée.
    Se fit aux noms de cellules définis dans la feuille de calcul.
    """

    omnivox_code = str(get_cell_value(ws, CTHM_OMNIVOX))
    comments = {}
    grades = {}

    collect_comment_grade(ws, eval, comments, grades)
    for c in eval.criteria:
        collect_comment_grade(ws, c, comments, grades)
        for i in c.indicators:
            collect_comment_grade(ws, i, comments, grades)

    # Gère les entrées vides
    ## Cas 1, total défini mais rien d'autre
    if (grades[eval.excel_id] is not None and
        all(v is None for k, v in grades.items() if k != eval.excel_id)):
        total = grades[eval.excel_id]
        for c in eval.criteria:
            grade = float(c.points) * total / float(eval.points)
            grades[c.excel_id] = grade
            for i in c.indicators:
                grades[i.excel_id] = float(i.points) * total / float(eval.points)
    ## Cas 2, critères définis mais rien pas les indicateurs
    else:
        for c in eval.criteria:
            if grades[c.excel_id] is None:
                continue
            total = grades[c.excel_id]
            if any(grades[i.excel_id] is not None for i in c.indicators):
                continue
            for i in c.indicators:
                grade = float(i.points) * total / float(c.points)
                grades[i.excel_id] = grade

    # Vérifie que les notes sont des nombres
    for k, v in grades.items():
        if v is None:
            raise ValueError(f"La note pour {k} doit être un nombre.")
        if not isinstance(v, int | float):
            raise ValueError(f"La note pour {k} doit être un nombre.")

    # Avertie si le total du critère est plus petit que la somme des indicateurs
    for c in eval.criteria:
        total = sum(grades[i.excel_id] for i in c.indicators if i.excel_id in grades)
        if total > grades[c.excel_id]:
            print(f"Avertissement : Dans la feuille {ws.title}, "
                  f"la somme des indicateurs pour le critère {c.name} "
                  f"est supérieure à la note du critère.")

    return GradeSheet(
        omnivox_code=omnivox_code,
        comments=comments,
        grades=grades,
    )

def collect_comment_grade(ws: Worksheet,
                      x : Evaluation | Criterion | Indicator,
                      comments: dict[str, str],
                      grades: dict[str, float | None]) -> None:
    c = get_cell_value(ws, comment_cell_name(x.excel_id))
    if c and str(c).strip():
        comments[x.excel_id] = str(c).strip()

    g = get_cell_value(ws, grade_cell_name(x.excel_id))
    if g is not None:
        grades[x.excel_id] = float(g) # type: ignore
    else:
        grades[x.excel_id] = None

def get_cell_value(ws: Worksheet,
                   name: str):
    cell = find_named_cell(ws, name)
    if cell is None:
        raise ValueError(f"La cellule nommée '{name}'"
                         f" n'existe pas dans la feuille {ws.title}.")
    if cell.value is None or str(cell.value).strip().upper() == "#N/A":
        return None
    return cell.value
