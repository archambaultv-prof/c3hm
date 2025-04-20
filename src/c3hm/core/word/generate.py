from pathlib import Path

import win32com.client as win32
from win32com.client import constants

from c3hm.core.rubric import Rubric

INCHES_TO_POINTS = 72

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

    # format lettre (8.5 x 11 pouces)
    doc.PageSetup.PaperSize = constants.wdPaperLetter

    # orientation paysage
    doc.PageSetup.Orientation = constants.wdOrientLandscape

    # marges moyennes selon Word

    doc.PageSetup.TopMargin = 1 * INCHES_TO_POINTS
    doc.PageSetup.BottomMargin = 1 * INCHES_TO_POINTS
    doc.PageSetup.LeftMargin = 0.75 * INCHES_TO_POINTS
    doc.PageSetup.RightMargin = 0.75 * INCHES_TO_POINTS

    # insérer numéro de page dans le pied de page
    # ajouter un pied de page
    footer = doc.Sections(1).Footers(constants.wdHeaderFooterPrimary)
    # ajouter un champ de numéro de page
    footer.PageNumbers.Add(
        constants.wdAlignPageNumberCenter, True
    )

    # insérer le titre
    endash = "\u2013"
    title = title = "Grille d'évaluation"
    if rubric.evaluation:
        title += f" {endash} {rubric.evaluation}"
    if rubric.course:
        title += f" {endash} {rubric.course}"
    p = doc.Paragraphs.Add()
    p.Range.Text = title
    p.Range.Style = constants.wdStyleHeading1
    p.Range.ParagraphFormat.Alignment = constants.wdAlignParagraphCenter
    p.Range.InsertParagraphAfter()

    # insérer la grille
    grid = rubric.grid
    nb_rows = grid.nb_rows()
    nb_columns = len(grid.scale) + 1  # +1 pour le critère
    table = doc.Tables.Add(
        doc.Range(doc.Content.End - 1),
        nb_rows,
        nb_columns,
        constants.wdWord8TableBehavior,
        constants.wdWord8TableBehavior,
    )

    # Remplir la première ligne avec le barème
    for i, scale in enumerate(grid.scale):
        table.Cell(1, i + 2).Range.Text = scale
        table.Cell(1, i + 2).Range.ParagraphFormat.Alignment = constants.wdAlignParagraphCenter
        table.Cell(1, i + 2).Range.Style = constants.wdStyleHeading3
    # Remplir le reste avec Critères et indicateurs dans l'ordre
    row = 2
    for criterion in grid.criteria:
        # Critère
        table.Cell(row, 1).Range.Text = criterion.name
        table.Cell(row, 1).Range.ParagraphFormat.Alignment = constants.wdAlignParagraphLeft
        table.Cell(row, 1).Range.Style = constants.wdStyleHeading3
        row += 1
        # Indicateurs
        for indicator in criterion.indicators:
            table.Cell(row, 1).Range.Text = indicator.name
            table.Cell(row, 1).Range.ParagraphFormat.Alignment = constants.wdAlignParagraphLeft
            row += 1

    # enregistrer et fermer
    doc.SaveAs(str(output_path))
    doc.Close(False)
    word.Quit()
