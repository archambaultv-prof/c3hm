import json
from pathlib import Path

from c3hm.data.rubric import Rubric


def export_template(output_path: Path, analytic: bool = False) -> None:
    """
    Génère une grille d'évaluation sous format Excel.
    """

    d = Rubric.template(analytic=analytic).to_dict()

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=4)

