import webbrowser
from pathlib import Path
from threading import Timer

from flask import Flask

from c3hm.server.routes import register_blueprints


def run_server(rubrics_dir: Path, port: int):
    """
    Lance le serveur Flask pour l'interface de correction interactive.
    """
    app = create_app(rubrics_dir)

    # Ouvrir le navigateur automatiquement après un court délai
    def open_browser():
        webbrowser.open(f"http://localhost:{port}")

    Timer(1.0, open_browser).start()

    # Lancer le serveur
    app.run(host="localhost", port=port, debug=False)


def create_app(rubrics_dir: Path) -> Flask:
    """
    Crée et configure l'application Flask.

    Args:
        rubrics_dir: Chemin vers le répertoire contenant les fichiers JSON des rubrics

    Returns:
        L'application Flask configurée
    """
    # Déterminer le chemin vers les templates et static
    server_dir = Path(__file__).parent

    app = Flask(__name__, template_folder=str(server_dir / "templates"), static_folder=str(server_dir / "static"))

    # Stocker le chemin des rubrics dans la config de l'app
    app.config["RUBRICS_DIR"] = rubrics_dir

    # Enregistrer les blueprints
    register_blueprints(app)

    return app
