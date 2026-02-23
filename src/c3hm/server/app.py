import json
import webbrowser
from pathlib import Path
from threading import Timer

from flask import Flask, jsonify, render_template, request

from c3hm.data.rubric import Rubric
from c3hm.data_typst import get_colors


def run_server(rubrics_dir: Path, port: int):
    """
    Lance le serveur Flask pour l'interface de correction interactive.

    Args:
        rubrics_dir: Répertoire contenant les fichiers JSON des rubrics
        port: Port sur lequel lancer le serveur
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
        rubrics_dir: Répertoire contenant les fichiers JSON des rubrics

    Returns:
        L'application Flask configurée
    """
    # Déterminer le chemin vers les templates et static
    server_dir = Path(__file__).parent

    app = Flask(
        __name__,
        template_folder=str(server_dir / "templates"),
        static_folder=str(server_dir / "static")
    )

    # Stocker le chemin des rubrics dans la config de l'app
    app.config["RUBRICS_DIR"] = rubrics_dir

    # Enregistrer les routes
    register_routes(app)

    return app


def register_routes(app: Flask):
    """
    Enregistre les routes de l'application Flask.
    """

    @app.route("/")
    def index():
        """Page d'accueil avec la liste des étudiants."""
        rubrics_dir = app.config["RUBRICS_DIR"]
        students_data = scan_rubrics(rubrics_dir)

        return render_template(
            "index.html",
            students=students_data,
            rubrics_dir=str(rubrics_dir),
            total_count=len(students_data),
            graded_count=sum(1 for s in students_data if s["graded"]),
            ungraded_count=sum(1 for s in students_data if not s["graded"])
        )

    @app.route("/api/students")
    def api_students():
        """API pour obtenir la liste des étudiants en JSON."""
        rubrics_dir = app.config["RUBRICS_DIR"]
        students_data = scan_rubrics(rubrics_dir)
        return jsonify(students_data)

    @app.route("/rubric/<filename>")
    def rubric(filename):
        """Page de correction d'une rubric."""
        rubrics_dir = app.config["RUBRICS_DIR"]
        json_files = sorted(rubrics_dir.glob("*.json"))
        filenames = [f.name for f in json_files]

        if filename not in filenames:
            return "Fichier non trouvé", 404

        return render_template(
            "rubric.html",
            filename=filename
        )

    @app.route("/api/rubric/<filename>")
    def api_rubric(filename):
        """API pour obtenir les données d'une rubric."""
        rubrics_dir = app.config["RUBRICS_DIR"]
        json_file = rubrics_dir / filename

        if not json_file.exists():
            return jsonify({"error": "Fichier non trouvé"}), 404

        try:
            with open(json_file, encoding="utf-8") as f:
                data = json.load(f)

            rubric = Rubric.from_dict(data)

            if rubric.student is None:
                return jsonify({"error": "Aucun étudiant dans cette rubric"}), 400

            return jsonify(rubric_to_dict(rubric, filename))

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/rubric/navigation/<filename>")
    def api_rubric_navigation(filename):
        """API pour obtenir les fichiers précédent et suivant."""
        rubrics_dir = app.config["RUBRICS_DIR"]
        json_files = sorted(rubrics_dir.glob("*.json"))
        filenames = [f.name for f in json_files]

        try:
            idx = filenames.index(filename)
            prev_filename = filenames[idx - 1] if idx > 0 else None
            next_filename = filenames[idx + 1] if idx < len(filenames) - 1 else None

            return jsonify({
                "previous": prev_filename,
                "next": next_filename,
                "current_index": idx,
                "total": len(filenames)
            })
        except ValueError:
            return jsonify({"error": "Fichier non trouvé"}), 404

    @app.route("/api/rubric/<filename>/save", methods=["POST"])
    def api_rubric_save(filename):
        """API pour sauvegarder les modifications d'une rubric."""
        rubrics_dir = app.config["RUBRICS_DIR"]
        json_file = rubrics_dir / filename

        if not json_file.exists():
            return jsonify({"error": "Fichier non trouvé"}), 404

        try:
            data = request.get_json()

            # Charger la rubric existante
            with open(json_file, encoding="utf-8") as f:
                rubric_data = json.load(f)

            # Mettre à jour les niveaux notés
            criteria = rubric_data.get("grille", {}).get("critères", [])
            updates = data.get("updates", {})  # Format: {"criterion_idx": {"indicator_idx": "level_label"}}

            for crit_idx_str, indicators in updates.items():
                crit_idx = int(crit_idx_str)
                if crit_idx < len(criteria):
                    for ind_idx_str, level_label in indicators.items():
                        ind_idx = int(ind_idx_str)
                        if ind_idx < len(criteria[crit_idx].get("indicateurs", [])):
                            criteria[crit_idx]["indicateurs"][ind_idx]["niveau noté"] = level_label

            # Mettre à jour les notes ajustées des critères
            criteria_overrides = _get_criteria_overrides(data)
            if isinstance(criteria_overrides, dict):
                for crit_idx_str, override_value in criteria_overrides.items():
                    try:
                        crit_idx = int(crit_idx_str)
                    except (TypeError, ValueError):
                        continue
                    if crit_idx < len(criteria):
                        _set_criterion_grade_override(criteria[crit_idx], override_value)

            # Mettre à jour le commentaire
            if "comment" in data:
                rubric_data["commentaire"] = data.get("comment", "")

            # Mettre à jour la note ajustée de la rubric
            rubric_override = _get_rubric_grade_override(data)
            if rubric_override is not _UNSET:
                _set_rubric_grade_override(rubric_data, rubric_override)

            # Mettre à jour les coéquipiers
            if "teammates" in data:
                old_teammates = rubric_data.get("coéquipiers", [])
                teammates = data.get("teammates", [])
                normalized_teammates = _normalize_teammates(teammates)
                rubric_data["coéquipiers"] = normalized_teammates

                current_student = rubric_data.get("étudiant", {})
                _sync_teammates(
                    rubrics_dir=rubrics_dir,
                    current_student=current_student,
                    new_teammates=normalized_teammates,
                    old_teammates=old_teammates,
                )

            # Sauvegarder le fichier
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(rubric_data, f, ensure_ascii=False, indent=2)

            return jsonify({"success": True, "message": "Rubric sauvegardée avec succès"})

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/rubric/<filename>/copy-to-teammates", methods=["POST"])
    def api_copy_to_teammates(filename):
        """Copie la grille, le commentaire et la note ajustée aux coéquipiers sélectionnés."""
        rubrics_dir = app.config["RUBRICS_DIR"]
        json_file = rubrics_dir / filename

        if not json_file.exists():
            return jsonify({"error": "Fichier non trouvé"}), 404

        try:
            payload = request.get_json()
            teammates = payload.get("teammates", [])
            normalized_teammates = _normalize_teammates(teammates)

            with open(json_file, encoding="utf-8") as f:
                source_data = json.load(f)

            current_student = source_data.get("étudiant", {})
            current_id = (current_student.get("matricule") or "").strip()
            old_teammates = source_data.get("coéquipiers", [])
            source_data["coéquipiers"] = normalized_teammates

            # Assurer la cohérence mutuelle des coéquipiers
            _sync_teammates(
                rubrics_dir=rubrics_dir,
                current_student=current_student,
                new_teammates=normalized_teammates,
                old_teammates=old_teammates,
            )

            student_index = _build_student_index(rubrics_dir)
            updated = []
            skipped = []

            for teammate in normalized_teammates:
                omnivox_id = (teammate.get("matricule") or "").strip()
                if not omnivox_id or omnivox_id not in student_index:
                    skipped.append(omnivox_id or "")
                    continue

                teammate_file = student_index[omnivox_id]
                try:
                    with open(teammate_file, encoding="utf-8") as tf:
                        teammate_data = json.load(tf)

                    _copy_grid_comment_and_grade(source_data, teammate_data)

                    if current_id:
                        teammate_data["coéquipiers"] = [
                            member
                            for member in [
                                {
                                    "prénom": current_student.get("prénom", ""),
                                    "nom": current_student.get("nom", ""),
                                    "matricule": current_id,
                                }
                            ] + normalized_teammates
                            if (member.get("matricule") or "").strip() != omnivox_id
                        ]

                    with open(teammate_file, "w", encoding="utf-8") as tf:
                        json.dump(teammate_data, tf, ensure_ascii=False, indent=2)

                    updated.append(omnivox_id)
                except Exception:
                    skipped.append(omnivox_id)

            return jsonify({"success": True, "updated": updated, "skipped": skipped})

        except Exception as e:
            return jsonify({"error": str(e)}), 500


def scan_rubrics(rubrics_dir: Path) -> list[dict]:
    """
    Scanne le répertoire de rubrics et extrait les informations des étudiants.

    Args:
        rubrics_dir: Répertoire contenant les fichiers JSON des rubrics

    Returns:
        Liste de dictionnaires contenant les informations des étudiants:
        - filename: nom du fichier JSON
        - student_name: nom complet de l'étudiant (prénom + nom)
        - first_name: prénom de l'étudiant
        - last_name: nom de famille de l'étudiant
        - graded: True si la rubric a au moins un indicateur noté
    """
    json_files = sorted(rubrics_dir.glob("*.json"))
    students = []

    for json_file in json_files:
        try:
            with open(json_file, encoding="utf-8") as f:
                data = json.load(f)

            rubric = Rubric.from_dict(data)

            # Vérifier si l'étudiant existe dans la rubric
            if rubric.student is None:
                continue

            # Déterminer si la rubric est corrigée (utiliser la méthode is_graded de Grid)
            graded = rubric.grid.is_graded()

            students.append({
                "filename": json_file.name,
                "student_name": f"{rubric.student.firstname} {rubric.student.surname}",
                "first_name": rubric.student.firstname,
                "last_name": rubric.student.surname,
                "omnivox_id": rubric.student.omnivox_id,
                "graded": graded
            })

        except Exception as e:
            # En cas d'erreur, on ignore ce fichier mais on continue
            print(f"⚠️  Erreur lors du traitement de {json_file.name}: {e}")

    return students


def rubric_to_dict(rubric: Rubric, filename: str) -> dict:
    """
    Convertit une rubric en dictionnaire pour le front-end.

    Args:
        rubric: La rubric à convertir
        filename: Le nom du fichier

    Returns:
        Dictionnaire contenant les données pour l'affichage
    """
    if rubric.student is None:
        raise ValueError("Cette rubric n'a pas d'étudiant associé")

    student_name = f"{rubric.student.firstname} {rubric.student.surname}"

    level_colors = get_colors(len(rubric.grid.levels))
    levels = [
        {
            "label": level.label,
            "percentage": level.percentage,
            "color": level_colors[idx]
        }
        for idx, level in enumerate(rubric.grid.levels)
    ]

    criteria = []
    for _, criterion in enumerate(rubric.grid.criteria):
        indicators = []
        for _, indicator in enumerate(criterion.indicators):
            # Trouver l'index du niveau noté
            graded_level_idx = None
            if indicator.graded_level:
                for level_idx, level in enumerate(rubric.grid.levels):
                    if level.match_label(indicator.graded_level):
                        graded_level_idx = level_idx
                        break

            indicators.append({
                "label": indicator.label,
                "points": indicator.points,
                "descriptors": indicator.descriptors,
                "graded_level": indicator.graded_level,
                "graded_level_idx": graded_level_idx
            })

        criteria.append({
            "label": criterion.label,
            "grade_override": criterion.grade_override,
            "indicators": indicators
        })

    return {
        "filename": filename,
        "student_name": student_name,
        "student": {
            "first_name": rubric.student.firstname,
            "last_name": rubric.student.surname,
            "omnivox_id": rubric.student.omnivox_id
        },
        "levels": levels,
        "grade_override": rubric.grade_override,
        "criteria": criteria,
        "teammates": [
            {
                "first_name": tm.firstname,
                "last_name": tm.surname,
                "omnivox_id": tm.omnivox_id
            }
            for tm in rubric.teammates
        ],
        "comment": rubric.comment if rubric.comment is not None else ""
    }


def _build_student_index(rubrics_dir: Path) -> dict[str, Path]:
    index: dict[str, Path] = {}
    for json_file in rubrics_dir.glob("*.json"):
        try:
            with open(json_file, encoding="utf-8") as f:
                data = json.load(f)
            rubric = Rubric.from_dict(data)
            if rubric.student is None:
                continue
            if rubric.student.omnivox_id:
                index[rubric.student.omnivox_id] = json_file
        except Exception:
            continue
    return index


def _copy_grid_comment_and_grade(source_data: dict, target_data: dict) -> None:
    source_grid = source_data.get("grille", {})
    target_grid = target_data.get("grille", {})
    source_criteria = source_grid.get("critères", [])
    target_criteria = target_grid.get("critères", [])

    for crit_idx, source_crit in enumerate(source_criteria):
        if crit_idx >= len(target_criteria):
            break
        _set_criterion_grade_override(target_criteria[crit_idx], _get_criterion_grade_override(source_crit))
        source_indicators = source_crit.get("indicateurs", [])
        target_indicators = target_criteria[crit_idx].get("indicateurs", [])
        for ind_idx, source_ind in enumerate(source_indicators):
            if ind_idx >= len(target_indicators):
                break
            target_indicators[ind_idx]["niveau noté"] = source_ind.get("niveau noté", "")

    if "commentaire" in source_data:
        target_data["commentaire"] = source_data.get("commentaire", "")

    if "note ajustée" in source_data:
        target_data["note ajustée"] = source_data.get("note ajustée")


class _UnsetType:
    pass


_UNSET = _UnsetType()


def _get_criteria_overrides(payload: dict) -> dict | None:
    for key in (
        "criterion_overrides",
        "criteria_overrides",
        "criterion_grade_overrides",
        "criteria_grade_overrides",
    ):
        value = payload.get(key)
        if value is not None:
            return value
    return None


def _get_rubric_grade_override(payload: dict) -> float | str | None | _UnsetType:
    for key in ("rubric_grade_override", "grade_override", "note_ajustee", "note ajustée"):
        if key in payload:
            return payload.get(key)
    return _UNSET


def _get_criterion_grade_override(criterion_data: dict) -> float | str | None:
    if "note" in criterion_data:
        return criterion_data.get("note")
    if "note ajustée" in criterion_data:
        return criterion_data.get("note ajustée")
    return None


def _set_criterion_grade_override(criterion_data: dict, override_value: float | str | None) -> None:
    if override_value is None or override_value == "":
        criterion_data.pop("note", None)
        criterion_data.pop("note ajustée", None)
        return
    criterion_data["note"] = override_value
    criterion_data["note ajustée"] = override_value


def _set_rubric_grade_override(rubric_data: dict, override_value: float | str | None) -> None:
    if override_value is None or override_value == "":
        rubric_data.pop("note ajustée", None)
        return
    rubric_data["note ajustée"] = override_value


def _normalize_teammates(teammates: list[dict]) -> list[dict]:
    normalized = []
    for tm in teammates:
        normalized.append({
            "prénom": tm.get("first_name", ""),
            "nom": tm.get("last_name", ""),
            "matricule": tm.get("omnivox_id", "")
        })
    return normalized


def _sync_teammates(
    rubrics_dir: Path,
    current_student: dict,
    new_teammates: list[dict],
    old_teammates: list[dict],
) -> None:
    current_id = (current_student.get("matricule") or "").strip()
    if not current_id:
        return

    student_index = _build_student_index(rubrics_dir)

    def teammate_id(entry: dict) -> str:
        return (entry.get("matricule") or "").strip()

    new_ids = {teammate_id(tm) for tm in new_teammates if teammate_id(tm)}
    old_ids = {teammate_id(tm) for tm in old_teammates if teammate_id(tm)}
    team_ids = new_ids | {current_id}

    team_members = [
        {
            "prénom": current_student.get("prénom", ""),
            "nom": current_student.get("nom", ""),
            "matricule": current_id,
        }
    ] + new_teammates

    # Mettre à jour tous les coéquipiers sélectionnés pour qu'ils aient la même liste.
    for teammate in new_teammates:
        tm_id = teammate_id(teammate)
        if not tm_id or tm_id not in student_index:
            continue

        teammate_file = student_index[tm_id]
        try:
            with open(teammate_file, encoding="utf-8") as tf:
                teammate_data = json.load(tf)

            teammate_data["coéquipiers"] = [
                member for member in team_members if teammate_id(member) != tm_id
            ]

            with open(teammate_file, "w", encoding="utf-8") as tf:
                json.dump(teammate_data, tf, ensure_ascii=False, indent=2)
        except Exception:
            continue

    # Nettoyer les anciens coéquipiers retirés pour eviter les liens non mutuels.
    removed_ids = old_ids - new_ids
    if removed_ids:
        for tm_id in removed_ids:
            if not tm_id or tm_id not in student_index:
                continue

            teammate_file = student_index[tm_id]
            try:
                with open(teammate_file, encoding="utf-8") as tf:
                    teammate_data = json.load(tf)

                existing = teammate_data.get("coéquipiers", [])
                filtered = [
                    tm for tm in existing if teammate_id(tm) not in team_ids
                ]
                teammate_data["coéquipiers"] = filtered

                with open(teammate_file, "w", encoding="utf-8") as tf:
                    json.dump(teammate_data, tf, ensure_ascii=False, indent=2)
            except Exception:
                continue
