from pathlib import Path

from jinja2 import Environment, PackageLoader

from c3hm.data.level import get_colors
from c3hm.data.rubric import Rubric


class TypstWriter:
    """
    Générateur de fichiers Typst à partir de rubriques.
    """

    def __init__(self, rubric: Rubric):
        self.rubric = rubric

        # Initialiser Jinja2 avec PackageLoader pour charger depuis c3hm.data.typst.templates
        loader = PackageLoader("c3hm.data.typst", "templates")
        self.env = Environment(loader=loader, trim_blocks=True, lstrip_blocks=True)

    def write_typst_file(self, output_path: Path) -> None:
        """
        Génère et écrit le fichier Typst.
        """
        template = self.env.get_template("rubric.typ.jinja")

        # Préparer les données pour le template
        nb_levels = len(self.rubric.grid.levels)
        colors = get_colors(nb_levels)
        columns_definition = ", ".join(["1fr"] * (nb_levels + 1))

        template_vars = {
            "rubric": self.rubric,
            "colors": colors,
            "columns_definition": columns_definition,
            "grid": self.rubric.grid,
            "student": self.rubric.student,
        }

        content = template.render(**template_vars)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
