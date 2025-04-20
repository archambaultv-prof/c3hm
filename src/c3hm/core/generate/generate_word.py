from importlib import resources
from pathlib import Path

import docx
import docx.enum.text
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

from c3hm.core.rubric import Rubric


def scale_color_schemes(size: int) -> list[str] | None:
    """
    Retourne une liste de couleurs format Word pour les cellules liées au barème.

    La première couleur est le vert parfait, la dernière est le rouge insuffisant.
    Prend en charge 2 à 5 niveaux de barème. Au-delà, renvoie None.
    """
    perfect_green   = "C8FFC8"  # RGB(200, 255, 200)
    very_good_green = "F0FFB0"  # RGB(240, 255, 176)
    half_way        = "FFF8C2"  # RGB(255, 248, 194)
    minimal_red     = "FFE4C8"  # RGB(255, 228, 200)
    bad_red         = "FFC8C8"  # RGB(255, 200, 200)

    color_schemes = {
        2: [perfect_green, bad_red],
        3: [perfect_green, half_way, bad_red],
        4: [perfect_green, very_good_green, half_way, bad_red],
        5: [perfect_green, very_good_green, half_way, minimal_red, bad_red],
    }
    return color_schemes.get(size)

def set_cell_background(cell, color_hex: str):
    """
    Définit la couleur de fond d'une cellule dans un document Word.
    """
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()

    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')         # shading style
    shd.set(qn('w:color'), 'auto')        # text color (auto = black/white depending on bg)
    shd.set(qn('w:fill'), color_hex)      # background color

    # remove old <w:shd> if any
    for old in tc_pr.findall(qn('w:shd')):
        tc_pr.remove(old)
    tc_pr.append(shd)

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

    # démarrer Word avec le modèle par défaut
    # Ce dernier contient déjà le formatage et les styles nécessaires
    template = resources.files("c3hm.assets.templates.word").joinpath("rubric-default.docx")
    with resources.as_file(template) as path:
        doc = docx.Document(path)

    # insérer le titre
    heading = doc.add_heading(rubric.title(), level=1)
    heading.alignment = docx.enum.text.WD_PARAGRAPH_ALIGNMENT.CENTER

    # insérer la grille
    grid = rubric.grid
    table = doc.add_table(rows=1, cols=grid.nb_columns(), style="Normal Table")

    # Remplir la première ligne avec le barème
    color_schemes = scale_color_schemes(len(grid.scale))
    hdr_cells = table.rows[0].cells
    for i, label in enumerate(grid.scale):
        cell = hdr_cells[i + 1]
        if color_schemes:
            set_cell_background(cell, color_schemes[i])
        p = cell.paragraphs[0]
        p.text = label
        p.style = "Heading 3"

    # Ajouter une bordure 1.5 de points en haut de la première ligne
    # top_border = table.Rows(1).Borders(constants.wdBorderTop)
    # top_border.LineStyle = constants.wdLineStyleSingle
    # top_border.LineWidth = constants.wdLineWidth150pt

    # bottom_border = table.Rows(1).Borders(constants.wdBorderBottom)
    # bottom_border.LineStyle = constants.wdLineStyleSingle
    # bottom_border.LineWidth = constants.wdLineWidth050pt

    # Répéter la première ligne en haut de chaque page
    # table.Rows(1).HeadingFormat = True

    # Remplir le reste avec Critères et indicateurs dans l'ordre
    for criterion in grid.criteria:
        row = table.add_row()
        # Critère
        p = row.cells[0].paragraphs[0]
        p.text = criterion.name
        p.style = "Heading 3"

        # Indicateurs
        for indicator in criterion.indicators:
            row = table.add_row()
            p = row.cells[0].paragraphs[0]
            run = p.add_run(indicator.name)
            run.style = "Emphasis"

            # Descripteurs alignés avec les niveaux de barème
            for i, descriptor in enumerate(indicator.descriptors):
                row.cells[i + 1].text = descriptor

    # # Ajouter une bordure 1.5 de points en bas de la dernière ligne
    # bottom_border = table.Rows(row_idx - 1).Borders(constants.wdBorderBottom)
    # bottom_border.LineStyle = constants.wdLineStyleSingle
    # bottom_border.LineWidth = constants.wdLineWidth150pt


    # enregistrer le fichier
    doc.save(output_path)
