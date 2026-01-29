import json
import subprocess
from pathlib import Path

from c3hm.data.rubric import Rubric
from c3hm.data.rubric_typst import TypstWriter


def export_rubric_from_json(input_path: Path, output_path: Path) -> None:
    with open(input_path, encoding="utf-8") as f:
        d = json.load(f)
    r = Rubric.from_dict(d)
    export_rubric(r, output_path)

def export_rubric(rubric: Rubric, output_path: Path) -> None:
    rubric.validate()
    output_suffix = output_path.suffix.lower()
    if output_suffix not in {".typ", ".pdf"}:
        raise ValueError(f"Le format de sortie '{output_suffix}' n'est pas supporté. Veuillez utiliser '.typ' ou '.pdf'.")

    # Write Typst file
    writer = TypstWriter(rubric)
    output_typst = output_path.with_suffix(".typ")
    writer.write_typst_file(output_typst)

    match output_suffix:
        case ".typ":
             # Rien à faire de plus
             pass
        case ".pdf":
            # Compile to PDF
            compile_typst_file(output_typst, output_path)
            output_typst.unlink()


def compile_typst_file(input_path: Path, output_path: Path) -> None:
    result = subprocess.run(
        ["typst", "compile", str(input_path), str(output_path)],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(f"Erreur lors de la compilation du fichier Typst:\n{result.stderr}")
