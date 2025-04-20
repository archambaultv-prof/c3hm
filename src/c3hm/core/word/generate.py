from pathlib import Path

import win32com.client as win32
from win32com.client import constants

from c3hm.core.rubric import Rubric


def generate_word_from_rubric(rubric: Rubric, output_path: Path | str) -> None:
    """
    Génère un document Word à partir d’une Rubric :
      - Orientation paysage
      - Numérotation des pages au centre du pied de page
      - Titre "{course} - {evaluation}"
      - Tableau : première ligne = barème (scale), puis une ligne par indicateur
        (les descriptors alignés avec les niveaux de barème)

    """
    output_path = Path(output_path)

    # forcer l'extension .docx
    if output_path.suffix.lower() != ".docx":
        output_path = output_path.with_suffix(".docx")

    # démarrer Word
    word = win32.gencache.EnsureDispatch("Word.Application")
    word.Visible = False
    doc = word.Documents.Add()

    # orientation paysage
    doc.PageSetup.Orientation = constants.wdOrientLandscape

    # insérer le titre
    emdash = "\u2014"
    title = rubric.course
    if not title:
        title = rubric.evaluation
    elif rubric.evaluation:
        title += f" {emdash} {rubric.evaluation}"
    if not title:
        title = "Grille d'évaluation"
    p = doc.Paragraphs.Add()
    p.Range.Text = title
    p.Range.Style = constants.wdStyleHeading1
    p.Range.InsertParagraphAfter()

    # numéroter les pages
    for section in doc.Sections:
        footer = section.Footers(constants.wdHeaderFooterPrimary)
        footer.PageNumbers.Add(
            PageNumberAlignment=constants.wdAlignPageNumberCenter
        )

    # préparer les données du tableau
    scale = rubric.grid.scale
    criteria = rubric.grid.criteria

    # nombre total de lignes = 1 ligne d'en‑tête + total des indicateurs
    total_rows = 1 + sum(len(crit.indicators) for crit in criteria)
    num_cols = len(scale)

    # insérer le tableau
    insert_range = doc.Range(doc.Content.End - 1, doc.Content.End - 1)
    table = doc.Tables.Add(insert_range, total_rows, num_cols)
    table.Borders.Enable = True

    # remplir la ligne d'en‑tête avec les labels du barème
    for col_idx, label in enumerate(scale, start=1):
        cell = table.Cell(1, col_idx)
        cell.Range.Text = label
        cell.Range.Bold = True
        cell.Shading.BackgroundPatternColor = constants.wdColorGray15

    # remplir les lignes suivantes : un rang par indicateur
    current_row = 2
    for crit in criteria:
        for ind in crit.indicators:
            for col_idx, descriptor in enumerate(ind.descriptors, start=1):
                table.Cell(current_row, col_idx).Range.Text = descriptor
            current_row += 1

    # enregistrer et fermer
    doc.SaveAs(str(output_path))
    doc.Close(False)
    word.Quit()
