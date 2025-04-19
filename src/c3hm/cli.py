import typer

from c3hm.commands.clean import clean_command
from c3hm.commands.rubric import rubric_app

app = typer.Typer(help="c3hm — Corriger à 3 heures du matin")

app.command(name="clean")(clean_command)
app.add_typer(rubric_app, name="rubric", help="Opérations sur les grilles d'évaluation")


def main():
    """
    Point d'entrée principal pour le package C3HM.
    """
    app()
