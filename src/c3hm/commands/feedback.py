from decimal import Decimal
from pathlib import Path

import openpyxl
from openpyxl import Workbook
from openpyxl.cell.cell import Cell
from openpyxl.worksheet.worksheet import Worksheet

from c3hm.commands.export.generate_rubric import generate_rubric
from c3hm.data.config import Config
from c3hm.data.evaluation.evaluation import Evaluation
from c3hm.data.student.student import Student
from c3hm.utils.decimal import round_to_nearest_quantum
from c3hm.utils.excel import (
    CTHM_EVAL_COMMENT,
    CTHM_EVAL_POINTS,
    CTHM_OMNIVOX,
    comment_cell_name,
    grade_cell_name,
)


def grades_from_wb(
    wb: Workbook,
    config: Config,
) -> list[Evaluation]:
    """
    Lit le fichier Excel et retourne une liste d'évaluations notées
    """
    evals = []

    # Si un étudiant est une référence d'équipe
    # - on lit sa feuille de calcul
    # - on lit la feuille de calcul des autres membres de l'équipe
    #   avec comme référence la première feuille de calcul.
    # Sinon on lit la feuille de calcul de l'étudiant seulement.
    for student in config.students:
        if student.is_team_reference:
            ws = find_worksheet(wb, student.alias)
            ref_eval = grades_from_ws(ws, config, None)
            evals.append(ref_eval)
            ls = config.students.find_other_team_members(student)
            for member in ls:
                ws = find_worksheet(wb, member.alias)
                team_eval = grades_from_ws(ws, config, ref_eval)
                evals.append(team_eval)
        elif not student.has_team():
            ws = find_worksheet(wb, student.alias)
            eval = grades_from_ws(ws, config, None)
            evals.append(eval)
    return evals

def find_worksheet(wb: Workbook, alias: str) -> Worksheet:
    """
    Trouve la feuille de calcul correspondant à l'alias de l'étudiant.
    Si la feuille n'existe pas, lève une erreur.
    """
    for ws in wb.worksheets:
        if ws.title == alias:
            return ws
    raise ValueError(f"La feuille de calcul pour l'alias '{alias}' n'existe pas.")

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
            try:
                cell = ws[coord]
            except IndexError as e:
                print(f"Erreur lors de la récupération de la cellule '{named_cell}'")
                print(f"Feuille : {ws.title}")
                raise e
            return cell

    return None


def grades_from_ws(ws: Worksheet,
                   config: Config,
                   reference: Evaluation | None) -> Evaluation:
    """
    Lit une feuille de calcul et retourne une évaluation notée.
    Se fit aux noms de cellules définis dans la feuille de calcul.
    """
    eval = config.rubric.evaluation.copy()

    # Récupère le code omnivox
    cell = find_named_cell(ws, CTHM_OMNIVOX)
    if cell is None:
        raise ValueError(f"La cellule nommée '{CTHM_OMNIVOX}' n'existe pas dans la feuille.")
    student = config.students.find_student(str(cell.value))
    if student is None:
        raise ValueError(f"Étudiant avec code omnivox '{cell.value}' "
                         "non trouvé dans la configuration.")
    eval.evaluated_student = student

    # Récupère le commentaire général
    cell = find_named_cell(ws, CTHM_EVAL_COMMENT)
    if cell is None:
        raise ValueError(f"La cellule nommée '{CTHM_EVAL_COMMENT}' "
                         "n'existe pas dans la feuille.")
    if cell.value is None and reference is not None:
        eval.comment = reference.comment
    elif cell.value is not None:
        eval.comment = str(cell.value).strip()
    else:
        eval.comment = ""

    # Récupère la note globale
    grade_cell = find_named_cell(ws, CTHM_EVAL_POINTS)
    if grade_cell is None:
        raise ValueError(f"La cellule nommée '{CTHM_EVAL_POINTS}' n'existe pas dans la feuille.")
    if cell_none_or_error(grade_cell) and reference is not None:
        eval.override_grade = reference.override_grade
    elif not cell_none_or_error(grade_cell):
        eval.override_grade = round_to_nearest_quantum(
            Decimal(str(grade_cell.value)),
            eval.grade_step)
    else:
        eval.override_grade = None

    # Récupère les notes et commentaires
    cs = reference.criteria if reference is not None else [None] * len(eval.criteria)
    for criterion, creference in zip(eval.criteria, cs, strict=True):
        grade_cell = find_named_cell(ws, grade_cell_name(criterion.id))
        if grade_cell is None:
            raise ValueError(f"La cellule nommée '{grade_cell_name(criterion.id)}'"
                             " n'existe pas dans la feuille.")
        if grade_cell.value is None:
            grade = creference.override_grade if creference is not None else None
        else:
            grade = round_to_nearest_quantum(Decimal(str(grade_cell.value)),
                                             eval.grade_step)
        criterion.override_grade = grade

        # Récupère les commentaires
        comment_cell = find_named_cell(ws, comment_cell_name(criterion.id))
        if comment_cell is None:
            raise ValueError(f"La cellule nommée '{comment_cell_name(criterion.id)}'"
                             " n'existe pas dans la feuille.")
        if comment_cell.value is None and creference is not None:
            comment = creference.comment
        elif comment_cell.value is not None:
            comment = str(comment_cell.value).strip()
        else:
            comment = ""
        criterion.comment = comment

        iss = (creference.indicators
               if creference is not None
               else [None] * len(criterion.indicators))
        for indicator, rindicator in zip(criterion.indicators, iss, strict=True):
            # Récupère la note de l'indicateur
            ind_grade_cell = find_named_cell(ws, grade_cell_name(indicator.id))
            if ind_grade_cell is None:
                raise ValueError(f"La cellule nommée '{grade_cell_name(indicator.id)}'"
                                 " n'existe pas dans la feuille.")
            if cell_none_or_error(ind_grade_cell) and rindicator is not None:
                ind_grade = rindicator.grade
            elif not cell_none_or_error(ind_grade_cell):
                ind_grade = round_to_nearest_quantum(Decimal(str(ind_grade_cell.value)),
                                                 eval.grade_step)
            else:
                raise ValueError(
                    f"La note de l'indicateur '{indicator.name}' n'est pas définie"
                    f" pour l'étudiant '{student.alias}'."
                )
            indicator.grade = ind_grade

            # Récupère le commentaire de l'indicateur
            ind_comment_cell = find_named_cell(ws, comment_cell_name(indicator.id))
            if ind_comment_cell is None:
                raise ValueError(f"La cellule nommée '{comment_cell_name(indicator.id)}'"
                                 " n'existe pas dans la feuille.")
            if ind_comment_cell.value is None and rindicator is not None:
                ind_comment = rindicator.comment
            elif ind_comment_cell.value is not None:
                ind_comment = str(ind_comment_cell.value).strip()
            else:
                ind_comment = ""
            indicator.comment = ind_comment


    return eval

def cell_none_or_error(cell: Cell) -> bool:
    return cell.value is None or str(cell.value).strip().upper() == "#N/A"


def generate_feedback(
    config_path: Path | str,
    gradebook_path: Path | str,
    output_dir: Path | str
) -> None:
    """
    Génère un document Word pour les étudiants à partir d’un grille d’évaluation (GradedRubric).
    """
    config_path = Path(config_path)
    gradebook_path = Path(gradebook_path)
    output_dir = Path(output_dir)

    config = Config.from_user_config(config_path)
    wb = openpyxl.load_workbook(gradebook_path,
                                data_only=True,
                                read_only=True)
    evaluations = grades_from_wb(wb, config)

    # Génère le document Word
    for eval in evaluations:
        student: Student = eval.evaluated_student # type: ignore
        # Génère le fichier dans le répertoire de sortie pour inspection manuelle
        feedback_path = output_dir / f"{student.omnivox_code}-{student.alias}.docx"
        feedback_path.parent.mkdir(parents=True, exist_ok=True)

        # Génère le document Word
        r = config.rubric.copy()
        r.evaluation = eval
        generate_rubric(r, feedback_path)

    # Génère le fichier Excel pour charge les notes dans Omnivox
    generate_xl_for_omnivox(config, evaluations, output_dir)


def generate_xl_for_omnivox(
    config: Config,
    evaluations: list[Evaluation],
    output_dir: Path | str
) -> None:
    """
    Génère un fichier Excel pour charger les notes dans Omnivox.
    """
    output_dir = Path(output_dir)
    omnivox_path = output_dir / f"{config.rubric.evaluation.name}.xlsx"
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Notes" # type: ignore

    # En-têtes
    ws.append(["Code omnivox", "Note", "Commentaire"]) # type: ignore

    # Remplit le tableau avec les notes et les commentaires
    for eval in evaluations:
        note = eval.get_grade()
        ws.append([eval.evaluated_student.omnivox_code, note, eval.comment]) # type: ignore

    # Sauvegarde le fichier Excel
    wb.save(omnivox_path)
