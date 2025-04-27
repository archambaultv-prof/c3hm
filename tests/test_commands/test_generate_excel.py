# from pathlib import Path

# from c3hm.core.generate.generate_excel import generate_excel_from_rubric
# from c3hm.core.rubric import load_rubric_from_xlsx


# def test_generate_excel_from_rubric(
#         rubric_template_5_path: Path,
#         tmp_path: Path,
#         output_dir: Path):
#     """
#     Teste la génération d'un document Excel à partir d'une grille d'évaluation.
#     Vérifie que le fichier est créé.

#     Recopie le fichier créé dans le répertoire tests/output pour inspection
#     manuelle si nécessaire.
#     """
#     r = load_rubric_from_xlsx(rubric_template_5_path)
#     name = rubric_template_5_path.with_name(
#         f"{rubric_template_5_path.stem}-out{rubric_template_5_path.suffix}")
#     xl_file = tmp_path / name
#     generate_excel_from_rubric(r, xl_file)
#     assert xl_file.exists()

#     # Copie le fichier dans le répertoire de sortie pour inspection manuelle
#     output_path = output_dir / xl_file.name
#     output_path.parent.mkdir(parents=True, exist_ok=True)
#     xl_file.replace(output_path)
