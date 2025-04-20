from pathlib import Path

# import win32api
# import win32com.client as win32
# from win32com.client import constants

from c3hm.core.rubric import Rubric

def generate_excel_from_rubric(rubric: Rubric, output_path: Path | str) -> None:
    """
    Génère un document Word à partir d’une Rubric :
      - Orientation paysage
      - Numérotation des pages au centre du pied de page
      - Titre "{course} - {evaluation}"
      - Tableau : première ligne = barème (scale), puis une ligne par indicateur
        (les descriptors alignés avec les niveaux de barème)

    """
    # output_path = Path(output_path)

    # # forcer l'extension .xlsx
    # if output_path.suffix.lower() != ".xlsx":
    #     output_path = output_path.with_suffix(".xlsx")

    # # démarrer Excel
    # excel = win32.gencache.EnsureDispatch("Excel.Application")
    # excel.Visible = False
    # workbook = excel.Workbooks.Add()
    # worksheet = workbook.Worksheets(1)

    # # Insérer le titre
    # worksheet.Cells(1, 1).Value = rubric.title()
    # worksheet.Cells(1, 1).Style = workbook.Styles("Heading 1")

    # # enregistrer et fermer
    # workbook.SaveAs(str(output_path))
    # workbook.Close(False)
    # excel.Quit()
    return None
