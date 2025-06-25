from decimal import Decimal
from pathlib import Path

import openpyxl
from openpyxl import Workbook
from openpyxl.cell.cell import Cell
from openpyxl.worksheet.worksheet import Worksheet

from c3hm.commands.generate_rubric import generate_rubric
from c3hm.data.config import Config
from c3hm.data.rubric import CTHM_GLOBAL_COMMENT, CTHM_GLOBAL_GRADE, CTHM_OMNIVOX
from c3hm.data.studentgrade import CriterionGrade, IndicatorGrade, StudentGrade
from c3hm.utils.decimal import round_to_nearest_quantum


def grades_from_wb(
    wb: Workbook,
    config: Config,
) -> list[StudentGrade]:
    """
    Lit le fichier Excel et retourne une liste de dictionnaires contenant
    les informations sur les grilles d'évaluation.
    Chaque dictionnaire contient les informations suivantes :
    - omnivox_code : le code omnivox de l'étudiant. Clé : cthm_omnivox
    - les notes et commentaires pour chaque critère et indicateur.
      Clé : le xl_cell_id_[grade|comment]
    """
    graded_rubrics = []

    # Si un étudiant est une référence d'équipe, on lit la feuille de calcul
    # de l'équipe et on ajoute les notes pour tous les membres de l'équipe.
    # Sinon on lit la feuille de calcul de l'étudiant seulement.
    for student in config.students:
        if student.is_team_reference:
            ws = find_worksheet(wb, student.alias)
            ref_grade = grades_from_ws(ws, config, None)
            graded_rubrics.append(ref_grade)
            ls = config.find_other_team_members(student)
            for member in ls:
                ws = find_worksheet(wb, member.alias)
                grade = grades_from_ws(ws, config, ref_grade)
                graded_rubrics.append(grade)
        elif not student.has_team():
            ws = find_worksheet(wb, student.alias)
            ref_grade = grades_from_ws(ws, config, None)
            graded_rubrics.append(ref_grade)
    return graded_rubrics

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
                   reference: StudentGrade | None) -> StudentGrade:
    """
    Lit une feuille de calcul et retourne un dictionnaire contenant
    les informations sur les grilles d'évaluation.
    Se fit aux noms de cellules définis dans la feuille de calcul.
    """
    rubric = config.rubric

    # Récupère le code omnivox
    cell = find_named_cell(ws, CTHM_OMNIVOX)
    if cell is None:
        raise ValueError(f"La cellule nommée '{CTHM_OMNIVOX}' n'existe pas dans la feuille.")
    student = config.find_student(str(cell.value))
    if student is None:
        raise ValueError(f"Étudiant avec code omnivox '{cell.value}' "
                         "non trouvé dans la configuration.")
    s = StudentGrade(student=student,
                     criteria=[],
                     comment="")

    # Récupère le commentaire général
    cell = find_named_cell(ws, CTHM_GLOBAL_COMMENT)
    if cell is None:
        raise ValueError(f"La cellule nommée '{CTHM_GLOBAL_COMMENT}' "
                         "n'existe pas dans la feuille.")
    if cell.value is None and reference is not None:
        s.comment = reference.comment
    elif cell.value is not None:
        s.comment = str(cell.value)
    else:
        s.comment = ""

    # Récupère la note globale
    grade_cell = find_named_cell(ws, CTHM_GLOBAL_GRADE)
    if grade_cell is None:
        raise ValueError(f"La cellule nommée '{CTHM_GLOBAL_GRADE}' n'existe pas dans la feuille.")
    if cell_none_or_error(grade_cell) and reference is not None:
        s.manual_grade = reference.manual_grade
    elif not cell_none_or_error(grade_cell):
        s.manual_grade = round_to_nearest_quantum(Decimal(str(grade_cell.value)),
                                                  rubric.precision)
    else:
        s.manual_grade = None

    # Récupère les notes et commentaires
    cs = reference.criteria if reference is not None else [None] * len(rubric.criteria)
    for criterion, creference in zip(rubric.criteria, cs, strict=True):
        c = CriterionGrade(
            indicators=[],
            manual_grade=None,
            percentage=criterion.percentage, # type: ignore
            comment=""
        )
        grade_cell = find_named_cell(ws, criterion.xl_grade_overwrite_cell_id())
        if grade_cell is None:
            raise ValueError(f"La cellule nommée '{criterion.xl_grade_overwrite_cell_id()}'"
                             " n'existe pas dans la feuille.")
        if grade_cell.value is None:
            if creference is not None:
                grade = creference.manual_grade
            grade = None
        else:
            grade = round_to_nearest_quantum(Decimal(str(grade_cell.value)),
                                            rubric.precision)
        c.manual_grade = grade

        # Récupère les commentaires
        comment_cell = find_named_cell(ws, criterion.xl_comment_cell_id())
        if comment_cell is None:
            raise ValueError(f"La cellule nommée '{criterion.xl_comment_cell_id()}'"
                             " n'existe pas dans la feuille.")
        if comment_cell.value is None and creference is not None:
            comment = creference.comment
        elif comment_cell.value is not None:
            comment = str(comment_cell.value).strip()
        else:
            comment = ""
        c.comment = comment

        iss = (creference.indicators
               if creference is not None
               else [None] * len(criterion.indicators))
        for indicator, rindicator in zip(criterion.indicators, iss, strict=True):
            # Récupère la note de l'indicateur
            ind_grade_cell = find_named_cell(ws, indicator.xl_grade_cell_id())
            if ind_grade_cell is None:
                raise ValueError(f"La cellule nommée '{indicator.xl_grade_cell_id()}'"
                                 " n'existe pas dans la feuille.")
            if cell_none_or_error(ind_grade_cell) and rindicator is not None:
                ind_grade = rindicator.grade
            elif not cell_none_or_error(ind_grade_cell):
                ind_grade = round_to_nearest_quantum(Decimal(str(ind_grade_cell.value)),
                                                 rubric.precision)
            else:
                raise ValueError(
                    f"La note de l'indicateur '{indicator.name}' n'est pas définie"
                    f" pour l'étudiant '{student.alias}'."
                )
            i = IndicatorGrade(
                grade=ind_grade,
                percentage=indicator.percentage,  # type: ignore
                comment=""
            )

            # Récupère le commentaire de l'indicateur
            ind_comment_cell = find_named_cell(ws, indicator.xl_comment_cell_id())
            if ind_comment_cell is None:
                raise ValueError(f"La cellule nommée '{indicator.xl_comment_cell_id()}'"
                                 " n'existe pas dans la feuille.")
            if ind_comment_cell.value is None and rindicator is not None:
                ind_comment = rindicator.comment
            elif ind_comment_cell.value is not None:
                ind_comment = str(ind_comment_cell.value).strip()
            else:
                ind_comment = ""
            i.comment = ind_comment
            c.indicators.append(i)
        # Ajoute le critère à la note de l'étudiant
        s.criteria.append(c)

    return s

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

    config = Config.from_yaml(config_path)
    wb = openpyxl.load_workbook(gradebook_path,
                                data_only=True,
                                read_only=True)
    grades = grades_from_wb(wb, config)

    # Génère le document Word
    for grade in grades:
        student = grade.student
        # Génère le fichier dans le répertoire de sortie pour inspection manuelle
        feedback_path = output_dir / f"{student.omnivox_code}-{student.alias}.docx"
        feedback_path.parent.mkdir(parents=True, exist_ok=True)

        # Génère le document Word
        course = config.evaluation.course or ""
        title = (student.first_name + " " +
                 student.last_name + " - " +
                 config.evaluation.name + " - " +
                 course)
        generate_rubric(config.rubric, feedback_path, title=title, grades=grade)
        # # Generate the PDF file
        # pdf_path = feedback_path.with_suffix(".pdf")
        # word_to_pdf(feedback_path, pdf_path)

    # Génère le fichier Excel pour charge les notes dans Omnivox
    generate_xl_for_omnivox(config, grades, output_dir)


def generate_xl_for_omnivox(
    config: Config,
    grades: list[StudentGrade],
    output_dir: Path | str
) -> None:
    """
    Génère un fichier Excel pour charger les notes dans Omnivox.
    """
    output_dir = Path(output_dir)
    omnivox_path = output_dir / f"{config.evaluation.name}.xlsx"
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Notes" # type: ignore

    # En-têtes
    ws.append(["Code omnivox", "Note", "Commentaire"]) # type: ignore

    # Remplit le tableau avec les notes et les commentaires
    for grade in grades:
        note = grade.rounded_grade(config.rubric.precision)
        ws.append([grade.student.omnivox_code, note, grade.comment]) # type: ignore

    # Sauvegarde le fichier Excel
    wb.save(omnivox_path)
