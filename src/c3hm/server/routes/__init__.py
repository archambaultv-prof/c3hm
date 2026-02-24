"""
Enregistrement des blueprints pour l'application Flask.
"""

from flask import Flask

from c3hm.server.routes.rubrics import rubrics_bp
from c3hm.server.routes.students import students_bp


def register_blueprints(app: Flask) -> None:
    """
    Enregistre tous les blueprints à l'application Flask.

    Args:
        app: L'application Flask
    """
    # Enregistrer les blueprints
    app.register_blueprint(students_bp)
    app.register_blueprint(rubrics_bp)
