import typer

from c3hm.typer.clean import clean_command
from c3hm.typer.feedback import feedback_command
from c3hm.typer.gradebook import gradebook_command
from c3hm.typer.statement import statement_rubric_command
from c3hm.typer.template import template_command

app = typer.Typer(help="c3hm — Corriger à 3 heures du matin")

app.command(name="clean")(clean_command)
app.command(name="rubric")(statement_rubric_command)
app.command(name="gradebook")(gradebook_command)
app.command(name="feedback")(feedback_command)
app.command(name="template")(template_command)

def main():
    """
    Point d'entrée principal pour le package C3HM.
    """
    app()
