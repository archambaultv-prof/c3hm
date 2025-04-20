from pathlib import Path

import win32api
import win32com.client as win32
from win32com.client import constants

from c3hm.core.rubric import Rubric

INCHES_TO_POINTS = 72

def scale_color_schemes(size: int) -> list[int] | None:
    """
    Retourne une liste de couleurs format Word pour les cellules liées au barème.

    La première couleur est le vert parfait, la dernière est le rouge insuffisant.
    Prend en charge 2 à 5 niveaux de barème. Au-delà, renvoie None.
    """
    perfect_green = win32api.RGB(200, 255, 200)
    very_good_green = win32api.RGB(240, 255, 176)
    half_way = win32api.RGB(255, 248, 194)
    minimal_red = win32api.RGB(255, 228, 200)
    bad_red = win32api.RGB(255, 200, 200)

    color_schemes = {
        2: [perfect_green, bad_red],
        3: [perfect_green, half_way, bad_red],
        4: [perfect_green, very_good_green, half_way, bad_red],
        5: [perfect_green, very_good_green, half_way, minimal_red, bad_red],
    }
    return color_schemes.get(size)

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
    nb_columns = grid.nb_columns()
    table = doc.Tables.Add(
        doc.Range(doc.Content.End - 1),
        nb_rows,
        nb_columns,
        constants.wdWord8TableBehavior,
        constants.wdWord8TableBehavior,
    )

    # Remplir la première ligne avec le barème
    color_schemes = scale_color_schemes(len(grid.scale))
    for i, scale in enumerate(grid.scale):
        table.Cell(1, i + 2).Range.Text = scale
        table.Cell(1, i + 2).Range.ParagraphFormat.Alignment = constants.wdAlignParagraphCenter
        table.Cell(1, i + 2).Range.Style = constants.wdStyleHeading3
        if color_schemes:
            table.Cell(1, i + 2).Shading.BackgroundPatternColor = color_schemes[i]
    # Ajouter une bordure 1.5 de points en haut de la première ligne
    top_border = table.Rows(1).Borders(constants.wdBorderTop)
    top_border.LineStyle = constants.wdLineStyleSingle
    top_border.LineWidth = constants.wdLineWidth150pt

    bottom_border = table.Rows(1).Borders(constants.wdBorderBottom)
    bottom_border.LineStyle = constants.wdLineStyleSingle
    bottom_border.LineWidth = constants.wdLineWidth050pt

    # Répéter la première ligne en haut de chaque page
    table.Rows(1).HeadingFormat = True

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
            table.Cell(row, 1).Range.Style = constants.wdStyleEmphasis

            # Descripteurs alignés avec les niveaux de barème
            for i, descriptor in enumerate(indicator.descriptors):
                table.Cell(row, i + 2).Range.Text = descriptor
                table.Cell(row, i + 2).Range.ParagraphFormat.Alignment = \
                    constants.wdAlignParagraphLeft

            row += 1
    # Ajouter une bordure 1.5 de points en bas de la dernière ligne
    bottom_border = table.Rows(row - 1).Borders(constants.wdBorderBottom)
    bottom_border.LineStyle = constants.wdLineStyleSingle
    bottom_border.LineWidth = constants.wdLineWidth150pt


    # enregistrer et fermer
    doc.SaveAs(str(output_path))
    doc.Close(False)
    word.Quit()
