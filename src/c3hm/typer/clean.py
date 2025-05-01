from pathlib import Path

import typer

from c3hm.commands.clean import PATHS_TO_DELETE, remove_unwanted_dirs


def clean_command(
    path: Path = typer.Argument(  # noqa: B008
        Path.cwd(),  # noqa: B008
        help="Répertoire racine contenant les dossiers des étudiants"
    ),
    dryrun: bool = typer.Option(
        False, "--dryrun", "-n",
        help="Simulation : affiche ce qui serait supprimé sans rien toucher"
    ),
    keep: list[str] = typer.Option(  # noqa: B008
        None, "--keep",
        help="Noms ou motifs (glob) à conserver alors qu'ils seraient normalement supprimés. "
             'Exemple : --keep ".git"'
    ),
    exclude_dir: list[str] = typer.Option(  # noqa: B008
        None, "--exclude-dir",
        help="Noms ou motifs (glob) de sous dossiers à exclure du nettoyage. "
             "c3hm ne va pas entrer dans ces dossiers. "
             'Exemple : --exclude "mon_dossier_12345"'
    ),
    delete: list[str] = typer.Option(  # noqa: B008
        None, "--delete",
        help="Noms ou motifs (glob) de fichiers ou dossiers supplémentaire à supprimer."
             'Exemple : --delete "*~"'
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v",
        help="Afficher chaque fichier/dossier supprimé"
    ),
    scan_all: bool = typer.Option(
        False, "--all", "-a",
        help="Scanner tous les fichiers et dossiers dans le répertoire racine, "
             "même ceux qui ne sont pas des dossiers d'étudiants."
    ),
):
    """
    Supprime les fichiers et dossiers indésirables (ex. .git, node_modules)
    dans chaque dossier étudiant sous PATH.

    Un dossier étudiant est un dossier qui respecte le format Omnivox: NOM1_NOM2_12345.

    Exemples d'utilisation :

      Nettoyage standard dans le répertoire courant

      > c3hm clean


      Simulation dans un répertoire spécifique

      > c3hm clean mon_dossier --dryrun

      Conserver les dossiers .git et .vscode

      > c3hm clean --keep ".git" --keep ".vscode"

      Nettoyage dans tous les dossiers, même ceux qui ne sont pas au format étudiant

      > c3hm clean --all
    """
    to_delete = PATHS_TO_DELETE.extend(delete)
    remove_unwanted_dirs(
        root_path=path,
        dryrun=dryrun,
        keep=keep,
        exclude_dir= exclude_dir,
        paths_to_delete=to_delete,
        verbose=verbose,
        scan_all=scan_all,
    )
    typer.echo("Nettoyage terminé.")
