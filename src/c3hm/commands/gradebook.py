from pathlib import Path

import openpyxl as pyxl
import openpyxl.utils as pyxl_utils
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import PatternFill
from openpyxl.utils import absolute_coordinate, quote_sheetname
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.worksheet.worksheet import Worksheet

from c3hm.commands.generate_rubric import scale_color_schemes
from c3hm.data.config import Config
from c3hm.data.rubric import CTHM_GLOBAL_COMMENT, CTHM_OMNIVOX, max_grade_weight
from c3hm.data.student import Student
from c3hm.utils import decimal_to_number


def generate_gradebook(config: Config, output_path: Path | str) -> None:
    """
    Génère un document Excel servant à la correction à partir d’une Rubric
    """
    if not config.students:
        raise ValueError("Aucun étudiant dans la configuration.")

    wb = pyxl.Workbook()
    for sheet in wb.worksheets:
        wb.remove(sheet)

    for student in config.students:
        # Crée une feuille pour chaque étudiant
        ws = wb.create_sheet(title=student.ws_name())
        add_student_sheet(ws, config, student)

    wb.save(output_path)

def add_student_sheet(ws: Worksheet, config: Config, student: Student) -> None:
    ws.sheet_view.showGridLines = False

    # Tailles de colonnes
    ws.column_dimensions['A'].width = 50
    ws.column_dimensions['B'].width = 15
    for i in range(3, 10):
        ws.column_dimensions[pyxl_utils.get_column_letter(i)].width = 15
    ws.column_dimensions[pyxl_utils.get_column_letter(10)].width = 60
    for i in range(11, 11 + len(config.rubric.grade_levels)):
        ws.column_dimensions[pyxl_utils.get_column_letter(i)].width = 15

    # Titre
    ws.append([config.title()])
    cell = ws.cell(row=ws.max_row, column=1)
    cell.style = "Title"
    ws.append([])

    # Info étudiant + commentaire général
    ws.append(["Étudiant", f"{student.first_name} {student.last_name}"])

    ws.append(["Code omnivox", f"{student.omnivox_code}"])
    cell = ws.cell(row=ws.max_row, column=2)
    dn = DefinedName(
        name=CTHM_OMNIVOX,
        attr_text=f"{quote_sheetname(ws.title)}!{absolute_coordinate(cell.coordinate)}",
    )
    ws.defined_names.add(dn)

    ws.append(["Commentaire général"])
    cell = ws.cell(row=ws.max_row, column=2)
    dn = DefinedName(
        name=CTHM_GLOBAL_COMMENT,
        attr_text=f"{quote_sheetname(ws.title)}!{absolute_coordinate(cell.coordinate)}",
    )
    ws.defined_names.add(dn)

    ws.append([])

    # Total sur X pts
    pts = "pt" if config.rubric.total == 1 else "pts"
    ws.append([f"Total sur {config.rubric.total} {pts}"])
    cell = ws.cell(row=ws.max_row, column=1)
    cell.style = "Headline 2"

    total_row = ws.max_row
    total_cell = 2
    cell = ws.cell(row=ws.max_row, column=2)
    cell.style = "Calculation"
    cell.number_format = "0.0"
    ws.append([])

    # Grille
    rubric = config.rubric

    # En-tête - barème
    col_before_scale = 1
    scale_colors = scale_color_schemes(len(rubric.grade_levels))
    extra_cols = ["note calculée", "note manuelle", "note", "commentaires",
                  "Poids critère / Note maximale par niveau"]
    ws.append([''] * col_before_scale + rubric.grade_levels + extra_cols)
    for i in range(col_before_scale + 1,
                   len(rubric.grade_levels) + col_before_scale + 1 + len(extra_cols)):
        cell = ws.cell(row=ws.max_row, column=i)
        cell.style = "Headline 4"
        if scale_colors and i - col_before_scale - 1 < len(scale_colors):
            color = scale_colors[i - col_before_scale - 1]
            cell.fill = PatternFill(start_color=color, end_color=color, fill_type="solid")


    criterion_rows = []
    computed_col = col_before_scale + len(rubric.grade_levels) + 1
    computed_letter = pyxl_utils.get_column_letter(computed_col)
    manual_col = col_before_scale + len(rubric.grade_levels) + 2
    manual_letter = pyxl_utils.get_column_letter(manual_col)
    final_col = col_before_scale + len(rubric.grade_levels) + 3
    final_letter = pyxl_utils.get_column_letter(final_col)
    comment_col = col_before_scale + len(rubric.grade_levels) + 4
    weight_col = col_before_scale + len(rubric.grade_levels) + 5
    weight_letter = pyxl_utils.get_column_letter(weight_col)
    for criterion in rubric.criteria:
        # Critère
        ws.append([criterion.name])
        cr = ws.max_row
        criterion_rows.append(cr)
        cell = ws.cell(row=ws.max_row, column=1)
        cell.style = "Headline 3"

        # Pondération du critère
        cell = ws.cell(row=ws.max_row, column=weight_col)
        cell.value = decimal_to_number(criterion.total)

        # note calculée
        cell = ws.cell(row=ws.max_row, column= computed_col)
        computed_range = (f"{computed_letter}{cr+1}:"
                          f"{computed_letter}{cr+len(criterion.indicators)}")
        criterion_weight_cell = (f"{weight_letter}{cr}")
        weight_range = (f"{weight_letter}{cr+1}:"
                        f"{weight_letter}{cr+len(criterion.indicators)}")
        cell.value = (f"=sum({computed_range})/sum({weight_range}) * {criterion_weight_cell}")
        cell.style = "Calculation"
        cell.number_format = "0.0"

        # note manuelle
        cell = ws.cell(row=ws.max_row, column= manual_col)
        cell.style = "Input"
        cell.number_format = "0.0"

        # note en pts
        cell = ws.cell(row=ws.max_row, column= col_before_scale + len(rubric.grade_levels) + 3)
        computed_or_manual = (f"=IF(ISBLANK({manual_letter}{cr}),{computed_letter}{cr},"
                              f"{manual_letter}{cr})")
        cell.value = computed_or_manual
        cell.style = "Calculation"
        cell.number_format = "0.0"
        dn = DefinedName(
            name=criterion.xl_grade_cell_id(),
            attr_text=f"{quote_sheetname(ws.title)}!{absolute_coordinate(cell.coordinate)}",
        )
        ws.defined_names.add(dn)

        # Commentaire
        cell = ws.cell(row=ws.max_row, column=comment_col)
        dn = DefinedName(
            name=criterion.xl_comment_cell_id(),
            attr_text=f"{quote_sheetname(ws.title)}!{absolute_coordinate(cell.coordinate)}",
        )
        ws.defined_names.add(dn)

        # Indicateurs
        for indicator in criterion.indicators:
            ws.append([indicator.name])

            for i in range(2):
                cell = ws.cell(row=ws.max_row, column=i+1)
                cell.style = "Explanatory Text"

            # Affichage conditionnel pour les indicateurs
            for i in range(len(indicator.descriptors)):
                color = "D3D3D3"  # Gris clair
                if scale_colors:
                    color = scale_colors[i]
                col_letter = pyxl_utils.get_column_letter(i + col_before_scale + 1)
                rule = FormulaRule(
                    formula=[f'NOT(ISBLANK({col_letter}{ws.max_row}))'],
                    stopIfTrue=True,
                    fill=PatternFill(start_color=color, end_color=color, fill_type="solid")
                )
                ws.conditional_formatting.add(
                    f'{col_letter}{ws.max_row}',
                    rule
                )

            # Ajout de la pondération de l'indicateur
            for i, gw in enumerate(indicator.grade_weights):
                cell = ws.cell(row=ws.max_row, column=i + weight_col)
                cell.value = decimal_to_number(max_grade_weight(gw))
                cell.style = "Explanatory Text"

            # Note pour l'indicateur.
            # Si on utilise une formule trop avancée, Excel
            # va ajouter un @ sur certains ranges, ce qui va casser la formule.
            # Donc on utilise des formules simples sans confusion avec les
            # dynamic arrays.
            r = ws.max_row
            def cell_addr(i, r=r):
                return f"{pyxl_utils.get_column_letter(i + col_before_scale + 1)}{r}"
            def thr_addr(i, r=r):
                return f"{pyxl_utils.get_column_letter(i + weight_col)}{r}"
            # one_cell est un test pour vérifier si uniquement une cellule est non vide
            one_cell = [f"IF(ISBLANK({cell_addr(i)}),0,1)"
                        for i in range(len(indicator.grade_weights))]
            one_cell = f"{' + '.join(one_cell)} = 1"
            # la note. Soit un nombre, soit la note maximale du niveau
            val = [f"IF(ISBLANK({cell_addr(i)}),0,"
                   f"IF(ISNUMBER({cell_addr(i)}),{cell_addr(i)},{thr_addr(i)}))"
                   for i in range(len(indicator.grade_weights))]
            val = f"{' + '.join(val)}"
            # Check si la note est supérieure à la note maximale
            # du niveau.
            val_check = f"IF({val} > {thr_addr(0)}, NA(), {val})"
            cell = ws.cell(row=ws.max_row, column=computed_col)
            cell.value = (f"=IF({one_cell},{val_check},NA())")
            cell.style = "Output"
            cell.number_format = "0.0"
            dn = DefinedName(
                name=indicator.xl_grade_cell_id(),
                attr_text=f"{quote_sheetname(ws.title)}!{absolute_coordinate(cell.coordinate)}",
            )
            ws.defined_names.add(dn)

            # Commentaire
            cell = ws.cell(row=ws.max_row, column=comment_col)
            dn = DefinedName(
                name=indicator.xl_comment_cell_id(),
                attr_text=f"{quote_sheetname(ws.title)}!{absolute_coordinate(cell.coordinate)}",
            )
            ws.defined_names.add(dn)

    # Formule pour le total
    f = "=sum("
    f += ",".join([f"{final_letter}{r}" for r in criterion_rows])
    f += ")"
    ws.cell(row=total_row, column=total_cell).value = f
