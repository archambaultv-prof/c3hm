from pathlib import Path

import click

from c3hm.commands.clean import PATHS_TO_DELETE, remove_unwanted_dirs


@click.command(
    name="clean",
    help=(
        "Supprime les fichiers et dossiers indésirables (ex. node_modules)\n"
        "dans chaque dossier étudiant sous PATH.\n\n"
        "Un dossier étudiant est un dossier qui respecte le format Omnivox: "
        "NOM1_NOM2_12345_REMIS_LE_.\n\n"
        "Enlève la partie _REMIS_LE_ du nom de dossier.\n\n"
        "Exemples:\n"
        "  c3hm clean .      # nettoie le répertoire courant\n"
        "  c3hm clean chemin/mon_dossier     # nettoie dans un dossier spécifique\n"
        "  c3hm clean chemin/mon_dossier -v   # nettoie dans un dossier spécifique et "
        "affiche les fichiers/dossiers supprimés\n"
        "  c3hm clean chemin/mon_dossier --dry-run # affiche les fichiers/dossiers "
        "qui seraient supprimés sans rien toucher\n"
    )
)
@click.argument(
    "path",
    type=click.Path(
        file_okay=False,
        dir_okay=True,
        path_type=Path
    ),
    required=True
)
@click.option(
    "--dry-run", "-n",
    is_flag=True,
    default=False,
    help="Simulation : affiche ce qui serait supprimé sans rien toucher. Active le mode verbose."
)
@click.option(
    "--git", "-g",
    is_flag=True,
    default=False,
    help="Supprimer les dossiers .git et .gitignore en plus des autres fichiers indésirables."
)

@click.option(
    "--verbose", "-v",
    is_flag=True,
    default=False,
    help="Afficher chaque fichier/dossier supprimé"
)

def clean_command(
    path: Path,
    dryrun: bool,
    git: bool,
    verbose: bool,
):
    """
    Supprime les fichiers et dossiers indésirables et renomme les dossiers étudiants
    """
    to_delete = PATHS_TO_DELETE
    if git:
        to_delete.extend([".git", ".gitignore"])
    remove_unwanted_dirs(
        root_path=path,
        dryrun=dryrun,
        exclude_dir=[],
        paths_to_delete=to_delete,
        verbose=verbose
    )
