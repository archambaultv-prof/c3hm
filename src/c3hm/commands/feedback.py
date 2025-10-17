from pathlib import Path

import openpyxl
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.worksheet.worksheet import Worksheet

from c3hm.commands.rubric.rubric_word import generate_rubric_word
from c3hm.data.config import Config
from c3hm.data.config_parser import check_all_grades, parse_user_config


def generate_feedback(gradebook_path: Path, output_dir: Path):
    """
    Génère un document Word de rétroaction pour les étudiants à partir d’une fichier de correction
    et un résumé des notes en format Excel.
    """
    configs: list[Config] = []
    for file in gradebook_path.glob("*.yaml"):
        try:
            config = parse_user_config(file, include_grading=True, check_grades=False)
            configs.append(config)
        except Exception as e:
            raise ValueError(f"Erreur lors de l'analyse du fichier {file}: {e}") from e

    _fill_in_teammates_grades(configs)

    for config in configs:
        try:
            check_all_grades(config)
        except Exception as e:
            raise ValueError("Erreur lors de la vérification des notes pour "
                             f"{config.student_first_name} {config.student_last_name}: {e}") from e

    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)
    if output_dir.is_file():
        raise NotADirectoryError(f"{output_dir} est un fichier et non un répertoire.")

    for config in configs:
        p = output_dir / (f"{config.student_omnivox}_{config.student_last_name}_"
                          f"{config.student_first_name}.docx")
        generate_rubric_word(config, p)

    # Génère le fichier Excel pour charger les notes dans Omnivox
    generate_xl_for_omnivox(configs, output_dir)


def generate_xl_for_omnivox(
    configs: list[Config],
    output_dir: Path | str
) -> None:
    """
    Génère un fichier Excel pour charger les notes dans Omnivox.
    """
    if not configs:
        return
    output_dir = Path(output_dir)
    omnivox_path = output_dir / f"{configs[0].evaluation_name}.xlsx"
    wb = openpyxl.Workbook()
    ws = wb.active
    if ws is None:
        raise ValueError("Aucune feuille de calcul active trouvée.")
    populate_omnivox_sheet(configs, ws)

    ws = wb.create_sheet()
    populate_averages_sheet(configs, ws)

    # Sauvegarde le fichier Excel
    wb.save(omnivox_path)

def populate_omnivox_sheet(configs: list[Config], ws: Worksheet) -> None:
    ws.title = "Notes pour Omnivox"
    ws.sheet_view.showGridLines = False  # Disable gridlines

    # En-têtes
    ws.append(["Code omnivox", "Note", "Commentaire", "Prénom", "Nom"])

    # Remplit le tableau avec les notes et les commentaires
    for config in configs:
        note = config.get_grade()
        comment = config.evaluation_comment
        ws.append([config.student_omnivox, note, comment,
                   config.student_first_name, config.student_last_name])

    # Format
    _insert_table(ws, "NotesOmnivox", "A1:E" + str(ws.max_row))
    ws.column_dimensions["A"].width = 20
    ws.column_dimensions["B"].width = 10
    ws.column_dimensions["C"].width = 70
    ws.column_dimensions["D"].width = 20
    ws.column_dimensions["E"].width = 20


def populate_averages_sheet(configs: list[Config], ws: Worksheet) -> None:

    ws.title = "Moyennes"
    ws.sheet_view.showGridLines = False  # Disable gridlines

    # Moyenne globale
    s = sum(c.get_grade() for c in configs)
    avg = s / len(configs)
    avg_percent = avg / configs[0].get_total()
    ws.append(["Moyenne globale"])
    ws.cell(ws.max_row, 1).style = "Headline 2"
    ws.append(["Évaluation", "Moyenne (pts)", "Moyenne (%)"])
    ws.append(["Évaluation",
               avg,
               avg_percent])
    _insert_table(ws, "MoyenneGlobale", "A2:C3")
    ws.append([])

    # Moyenne par critères
    ws.append(["Moyenne par critères"])
    ws.cell(ws.max_row, 1).style = "Headline 2"
    crit_header_row = ws.max_row + 1
    ws.append(["Critère", "Moyenne (pts)", "Moyenne (%)"])
    crit_count = len(configs[0].criteria)
    for i in range(crit_count):
        s = sum(c.criteria[i].get_grade() for c in configs)
        avg = s / len(configs)
        avg_percent = avg / configs[0].criteria[i].get_total()
        ws.append([configs[0].criteria[i].name,
                   avg,
                   avg_percent])
    # Transforme les données en table
    _insert_table(ws, "MoyenneCriteres", f"A{crit_header_row}:C{crit_header_row + crit_count}")
    ws.append([])

    # Moyenne par indicateurs
    ws.append(["Moyenne par indicateurs"])
    ws.cell(ws.max_row, 1).style = "Headline 2"
    ind_header_row = ws.max_row + 1
    ws.append(["Indicateur", "Moyenne (pts)", "Moyenne (%)", "Critère"])
    ind_total_count = 0
    for c_idx in range(crit_count):
        ind_total_count += len(configs[0].criteria[c_idx].indicators)
        c_name = configs[0].criteria[c_idx].name
        for i_idx in range(len(configs[0].criteria[c_idx].indicators)):
            ind_name = configs[0].criteria[c_idx].indicators[i_idx].name
            s = sum(c.criteria[c_idx].indicators[i_idx].get_grade() for c in configs)
            avg = s / len(configs)
            avg_percent = avg / configs[0].criteria[c_idx].indicators[i_idx].get_total()
            ws.append([ind_name,
                       avg,
                       avg_percent,
                       c_name])
    # Transforme les données en table
    _insert_table(ws, "MoyenneIndicateurs",
                  f"A{ind_header_row}:D{ind_header_row + ind_total_count}")

    # Applique les formats: pts = 0.0, % = 0.0%
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
        # Colonne B (pts)
        if len(row) > 1 and isinstance(row[1].value, int | float):
            row[1].number_format = '0.0'
        # Colonne C (%)
        if len(row) > 2 and isinstance(row[2].value, int | float):
            row[2].number_format = '0.0%'
    ws.column_dimensions["A"].width = 60
    ws.column_dimensions["B"].width = 15
    ws.column_dimensions["C"].width = 15
    ws.column_dimensions["D"].width = 60


def _insert_table(ws: Worksheet, display_name: str, ref: str) -> None:
    table = Table(displayName=display_name, ref=ref)
    table.tableStyleInfo = TableStyleInfo(
        name="TableStyleMedium2",
        showFirstColumn=False,
        showLastColumn=False,
        showRowStripes=True,
        showColumnStripes=False
    )
    ws.add_table(table)

def _fill_in_teammates_grades(configs: list[Config]) -> None:
    """
    Remplit les notes des coéquipiers dans chaque configuration.
    """
    known_configs: dict[str, Config] = {}
    duplicate_names: set[str] = set()
    for config in configs:
        for k in (config.student_first_name, config.student_last_name,
                  f"{config.student_first_name} {config.student_last_name}",
                  f"{config.student_last_name} {config.student_first_name}"):
            if k is None:
                continue
            k = k.lower().strip()
            if k in duplicate_names:
                continue
            if k in known_configs:
                del known_configs[k]
                duplicate_names.add(k)
            else:
                known_configs[k] = config

    done: set[str] = set()
    for config in configs:
        for teammate in config.student_teammates:
            teammate = teammate.lower().strip()
            if teammate in known_configs:
                target_config = known_configs[teammate]
                if target_config.get_student_full_name() in done:
                    raise ValueError(f"La configuration de {target_config.student_first_name} "
                                     f"{target_config.student_last_name} a déjà été ajustée "
                                     f"depuis un autre coéquipier.")
                done.add(target_config.get_student_full_name())
                _copy_grades_to(config, target_config)
            elif teammate in duplicate_names:
                raise ValueError(f"Le nom de coéquipier '{teammate}' est ambigu dans la "
                                 f"configuration de {config.student_first_name} "
                                 f"{config.student_last_name}.")
            else:
                raise ValueError(f"Le coéquipier '{teammate}' de la configuration de "
                                 f"{config.student_first_name} {config.student_last_name} "
                                 f"n'a pas été trouvé dans les configurations fournies.")

def _copy_grades_to(source: Config, target: Config) -> None:
    """
    Copie les notes des critères et indicateurs de `source` vers `target`.
    """
    if target.evaluation_grade is None:
        target.evaluation_grade = source.evaluation_grade
    if target.evaluation_comment is None:
        target.evaluation_comment = source.evaluation_comment
    for source_criterion, target_criterion in zip(source.criteria, target.criteria, strict=True):
        if source_criterion.name != target_criterion.name:
            raise ValueError(f"Les critères '{source_criterion.name}' et "
                             f"'{target_criterion.name}' ne correspondent pas.")
        if target_criterion.grade is None:
            target_criterion.grade = source_criterion.grade
        if target_criterion.comment is None:
            target_criterion.comment = source_criterion.comment
        for source_indicator, target_indicator in zip(source_criterion.indicators,
                                                     target_criterion.indicators, strict=True):
            if source_indicator.name != target_indicator.name:
                raise ValueError(f"Les indicateurs '{source_indicator.name}' et "
                                 f"'{target_indicator.name}' ne correspondent pas.")
            if target_indicator.grade is None:
                target_indicator.grade = source_indicator.grade
            if target_indicator.comment is None:
                target_indicator.comment = source_indicator.comment
