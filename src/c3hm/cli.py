import typer

from c3hm.typer.clean import clean_command
from c3hm.typer.feedback import feedback_command
from c3hm.typer.gradebook import gradebook_command
from c3hm.typer.student import student_command

app = typer.Typer(help="c3hm — Corriger à 3 heures du matin")

app.command(name="clean")(clean_command)
app.command(name="student")(student_command)
app.command(name="gradebook")(gradebook_command)
app.command(name="feedback")(feedback_command)

def main():
    """
    Point d'entrée principal pour le package C3HM.
    """
    app()
