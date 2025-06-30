import openpyxl.utils as pyxl_utils
from openpyxl.utils import absolute_coordinate, quote_sheetname
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.worksheet.worksheet import Worksheet

CTHM_OMNIVOX = "cthm_code_omnivox"

def safe_for_named_cell(s: str):
    """
    Vérifie si une chaîne de caractères est sûre pour être utilisée comme nom de cellule Excel.
    """
    # Seulement a-z, A-Z, _, 0-9, et ne commence pas par un chiffre
    if not s or not s[0].isalpha():
        return False
    if s in [CTHM_OMNIVOX]:
        return False
    return all(c.isalnum() or c == "_" for c in s)

def grade_cell_name(id: str):
    """
    Retourne un nom de cellule Excel pour une note.
    """
    if not safe_for_named_cell(id):
        raise ValueError(f"Le nom '{id}' n'est pas sûr pour une cellule Excel.")
    return "cthm_" + id + "_points"

def comment_cell_name(id: str):
    """
    Retourne un nom de cellule Excel pour un commentaire.
    """
    if not safe_for_named_cell(id):
        raise ValueError(f"Le nom '{id}' n'est pas sûr pour une cellule Excel.")
    return "cthm_" + id + "_commentaire"

def define_ws_named_cell(ws: Worksheet, row: int, col: int, name: str):
    """
    Définit un nom de cellule dans la feuille de calcul.
    """
    cell = ws.cell(row=row, column=col)
    dn = DefinedName(
        name=name,
        attr_text=f"{quote_sheetname(ws.title)}!{absolute_coordinate(cell.coordinate)}",
    )
    ws.defined_names.add(dn)

def cell_addr(row: int, col: int, ws: Worksheet | str | None = None) -> str:
    """
    Retourne l'adresse d'une cellule Excel à partir de la ligne et de la colonne.
    """
    if isinstance(ws, Worksheet):
        ws = ws.title
    ws_name = f"{quote_sheetname(ws)}!" if ws is not None else ""
    return f"{ws_name}{pyxl_utils.get_column_letter(col)}{row}"
