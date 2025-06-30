from docx.document import Document
from docx.enum.section import WD_ORIENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm
from docx.table import Table


def set_as_table_header(row):
    """
    Définit la ligne d'un tableau Word comme en-tête répétée sur chaque page.
    """
    tr = row._tr
    tr_pr = tr.get_or_add_trPr()

    tbl_header = OxmlElement('w:tblHeader')
    tbl_header.set(qn('w:val'), 'true')
    tr_pr.append(tbl_header)

def set_cell_background(cell, color_hex: str):
    """
    Définit la couleur de fond d'une cellule dans un tableau Word.
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

def set_row_borders(row, top: float | None =0.5, bottom: float | None =0.5):
    """
    Définit les bordures hautes et basses d'une ligne dans un tableau Word.
    """
    def set_border(tc_borders, side, width_pt):
        border = tc_borders.find(qn(f'w:{side}'))
        if border is None:
            border = OxmlElement(f'w:{side}')
            tc_borders.append(border)
        border.set(qn('w:val'), 'single')
        border.set(qn('w:sz'), str(int(width_pt * 8)))  # Word uses 1/8 pt units
        border.set(qn('w:space'), "0")

    for cell in row.cells:
        tc = cell._tc
        tc_pr = tc.get_or_add_tcPr()
        tc_borders = tc_pr.find(qn('w:tcBorders'))
        if tc_borders is None:
            tc_borders = OxmlElement('w:tcBorders')
            tc_pr.append(tc_borders)

        if top:
            set_border(tc_borders, 'top', top)
        if bottom:
            set_border(tc_borders, 'bottom', bottom)

def set_orientation(doc: Document, orientation: str):
    """
    Définit l'orientation de la page dans un document Word.
    """
    sections = doc.sections
    for section in sections:
        if orientation == "paysage":
            section.orientation = WD_ORIENT.LANDSCAPE
            # Échanger la largeur et la hauteur de la page
            if section.page_width < section.page_height: # type: ignore
                section.page_width, section.page_height = (
                    section.page_height,
                    section.page_width,
                )
        elif orientation == "portrait":
            section.orientation = WD_ORIENT.PORTRAIT
            # Échanger la largeur et la hauteur de la page
            if section.page_width > section.page_height: # type: ignore
                section.page_width, section.page_height = (
                    section.page_height,
                    section.page_width,
                )
        else:
            raise ValueError(f"Orientation '{orientation}' non valide. "
                             "Utilisez 'paysage' ou 'portrait'.")


def add_word_table(doc: Document, n_cols: int, column_widths_cm: list[float|None]) -> Table:
    """
    Insère un tableau à n_cols colonnes, en utilisant largeurs_cm pour définir
    la largeur de chaque colonne en cm. Les valeurs None partagent
    équitablement l’espace restant.
    """
    # 1) Création du tableau
    table = doc.add_table(rows=1, cols=n_cols, style="Normal Table")
    if not column_widths_cm:
        return table

    table.autofit = False  # désactive l’ajustement automatique de Word

    # 2) Calcul de la largeur disponible en EMU
    sect = doc.sections[0]
    avail_width_emu = (
        sect.page_width
        - sect.left_margin # type: ignore
        - sect.right_margin
    )

    # 3) Conversion des spécifications cm en EMU
    fixed_emu = [Cm(w) for w in column_widths_cm if w is not None]
    total_fixed = sum(fixed_emu)

    # Décompte du nombre de colonnes à largeur automatique
    nb_auto = sum(1 for w in column_widths_cm if w is None)
    emu_auto = (
        (avail_width_emu - total_fixed) // nb_auto
        if nb_auto else 0
    )

    # 4) Assignation de la largeur à chaque colonne
    for idx, col in enumerate(table.columns):
        w = column_widths_cm[idx]
        col.width = Cm(w) if w is not None else emu_auto # type: ignore

    # 5) Assignation de la largeur à chaque cellule
    # (yep ... c'est comme ça dans Word)
    for row in table.rows:
        for idx, cell in enumerate(row.cells):
            w = column_widths_cm[idx]
            cell.width = Cm(w) if w is not None else emu_auto # type: ignore

    return table
