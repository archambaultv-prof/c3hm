from pathlib import Path

import typer

rubric_app = typer.Typer(help="Opérations sur les grilles d'évaluation")

@rubric_app.command("generate")
def generate(
    input_yaml: Path = typer.Argument(  # noqa: B008
        ...,
        help="Chemin vers le fichier de définition de la grille (YAML)"
    ),
    output: str | None = typer.Option(
        None,
        "--output", "-o",
        help="Nom de base pour tous les fichiers générés "
             "(par défaut : nom du fichier YAML sans extension)"
    ),
    student_format: list[str] = typer.Option(  # noqa: B008
        [".docx"],
        "--student-format", "-sf",
        help=(
            "Format(s) de sortie pour les étudiants. Répétable. "
            "Valeurs possibles : '.docx', '.pdf', '.md'"
        )
    ),
    no_teacher_file: bool = typer.Option(  # noqa: B008
        False,
        "--no-teacher-file",
        help="Ne pas générer le fichier de correction pour l’enseignant"
    ),
    outdir: Path = typer.Option(  # noqa: B008
        Path.cwd(),  # noqa: B008
        "--outdir", "-d",
        help="Répertoire où écrire les fichiers générés (par défaut : répertoire courant)"
    ),
):
    """
    Génère les fichiers de grille à partir d'une définition YAML.

    Cette commande lit INPUT_YAML et produit :

      - Une copie pour les étudiants aux formats précisés par --student-format
        (par défaut : .docx)

      - Un tableur Excel pour la correction

    Exemples :

      Par défaut : .docx pour étudiants, .xlsx pour enseignant

      > c3hm rubric generate tp2.yaml

      Nom personnalisé + répertoire de sortie

      > c3hm rubric generate tp2.yaml -o "TP 2" -d "Mon dossier"

      Word + PDF pour les étudiants

      > c3hm rubric generate tp2.yaml --student-format ".docx" --student-format ".pdf"

      Uniquement Markdown pour les étudiants, sans fichier enseignant

      > c3hm rubric generate tp2.yaml --student-format ".md" --no-teacher-file
    """
    # TODO : implémenter la logique de génération ici
    pass
