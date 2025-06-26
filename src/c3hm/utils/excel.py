def safe_for_named_cell(s: str):
    """
    Vérifie si une chaîne de caractères est sûre pour être utilisée comme nom de cellule Excel.
    """
    # Seulement a-z, A-Z, _, 0-9, et ne commence pas par un chiffre
    if not s or not s[0].isalpha():
        return False
    return all(c.isalnum() or c == "_" for c in s)

def grade_cell_name(id: str):
    """
    Retourne un nom de cellule Excel pour une note.
    """
    if not safe_for_named_cell(id):
        raise ValueError(f"Le nom '{id}' n'est pas sûr pour une cellule Excel.")
    return id + "_grade"

def comment_cell_name(id: str):
    """
    Retourne un nom de cellule Excel pour un commentaire.
    """
    if not safe_for_named_cell(id):
        raise ValueError(f"Le nom '{id}' n'est pas sûr pour une cellule Excel.")
    return id + "_commentaire"
