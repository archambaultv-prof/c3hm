import click

from c3hm.cli.export import export_rubric_command
from c3hm.cli.feedback import feedback_command
from c3hm.cli.gradebook import gradebook_command
from c3hm.cli.template import template_command
from c3hm.cli.unpack import unpack_command


@click.group(help="c3hm — Corriger à 3 heures du matin")
def cli():
    """
    Point d'entrée principal pour la CLI de c3hm.
    """
    pass

# Ajout des commandes à la CLI
cli.add_command(unpack_command)
cli.add_command(template_command)
cli.add_command(export_rubric_command)
cli.add_command(gradebook_command)
cli.add_command(feedback_command)

def main():
    """
    Point d'entrée principal pour le package C3HM.
    """
    cli()
