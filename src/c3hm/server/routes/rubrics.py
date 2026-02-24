"""
Blueprint pour les routes liées aux rubrics (correction, API).
"""

import json

from flask import Blueprint, current_app, jsonify, render_template, request

from c3hm.data import (
    JSON_KEY_COMMENT,
    JSON_KEY_CRITERIA,
    JSON_KEY_FIRSTNAME,
    JSON_KEY_GRADED_LEVEL,
    JSON_KEY_GRID,
    JSON_KEY_INDICATORS,
    JSON_KEY_LASTNAME,
    JSON_KEY_OMNIVOX_ID,
    JSON_KEY_STUDENT,
    JSON_KEY_TEAMMATES,
)
from c3hm.server.config import COMMENT_KEY, TEAMMATES_KEY, UNSET
from c3hm.server.persistence import RubricRepository
from c3hm.server.services import GradeManager, StudentService, TeammateManager
from c3hm.server.transformers import RubricSerializer

rubrics_bp = Blueprint("rubrics", __name__)


@rubrics_bp.route("/rubric/<filename>")
def rubric(filename):
    """Page de correction d'une rubric."""
    rubrics_dir = current_app.config["RUBRICS_DIR"]
    repository = RubricRepository(rubrics_dir)
    filenames = repository.list_filenames()

    if filename not in filenames:
        return "Fichier non trouvé", 404

    return render_template("rubric.html", filename=filename)


@rubrics_bp.route("/api/rubric/<filename>")
def api_rubric(filename):
    """API pour obtenir les données d'une rubric."""
    rubrics_dir = current_app.config["RUBRICS_DIR"]
    repository = RubricRepository(rubrics_dir)

    if not repository.file_exists(filename):
        return jsonify({"error": "Fichier non trouvé"}), 404

    try:
        rubric = repository.load_rubric_object(filename)

        if rubric.student is None:
            return jsonify({"error": "Aucun étudiant dans cette rubric"}), 400

        return jsonify(RubricSerializer.to_dict(rubric, filename))

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@rubrics_bp.route("/api/rubric/navigation/<filename>")
def api_rubric_navigation(filename):
    """API pour obtenir les fichiers précédent et suivant."""
    rubrics_dir = current_app.config["RUBRICS_DIR"]
    repository = RubricRepository(rubrics_dir)
    filenames = repository.list_filenames()

    try:
        idx = filenames.index(filename)
        prev_filename = filenames[idx - 1] if idx > 0 else None
        next_filename = filenames[idx + 1] if idx < len(filenames) - 1 else None

        return jsonify(
            {"previous": prev_filename, "next": next_filename, "current_index": idx, "total": len(filenames)}
        )
    except ValueError:
        return jsonify({"error": "Fichier non trouvé"}), 404


@rubrics_bp.route("/api/rubric/<filename>/save", methods=["POST"])
def api_rubric_save(filename):
    """API pour sauvegarder les modifications d'une rubric."""
    rubrics_dir = current_app.config["RUBRICS_DIR"]
    repository = RubricRepository(rubrics_dir)

    if not repository.file_exists(filename):
        return jsonify({"error": "Fichier non trouvé"}), 404

    try:
        data = request.get_json()

        # Charger la rubric existante
        rubric_data = repository.load_rubric(filename)

        # Mettre à jour les niveaux notés
        criteria = rubric_data.get(JSON_KEY_GRID, {}).get(JSON_KEY_CRITERIA, [])
        updates = data.get("updates", {})  # Format: {"criterion_idx": {"indicator_idx": "level_label"}}

        for crit_idx_str, indicators in updates.items():
            crit_idx = int(crit_idx_str)
            if crit_idx < len(criteria):
                for ind_idx_str, level_label in indicators.items():
                    ind_idx = int(ind_idx_str)
                    if ind_idx < len(criteria[crit_idx].get(JSON_KEY_INDICATORS, [])):
                        criteria[crit_idx][JSON_KEY_INDICATORS][ind_idx][JSON_KEY_GRADED_LEVEL] = level_label

        # Mettre à jour les notes ajustées des critères
        criteria_overrides = GradeManager.get_criteria_overrides(data)
        if isinstance(criteria_overrides, dict):
            for crit_idx_str, override_value in criteria_overrides.items():
                try:
                    crit_idx = int(crit_idx_str)
                except (TypeError, ValueError):
                    continue
                if crit_idx < len(criteria):
                    GradeManager.set_criterion_override(criteria[crit_idx], override_value)

        # Mettre à jour le commentaire
        if COMMENT_KEY in data:
            rubric_data[JSON_KEY_COMMENT] = data.get(COMMENT_KEY, "")

        # Mettre à jour la note ajustée de la rubric
        rubric_override = GradeManager.get_rubric_grade_override(data)
        if rubric_override is not UNSET:
            GradeManager.set_rubric_override(rubric_data, rubric_override)

        # Mettre à jour les coéquipiers
        if TEAMMATES_KEY in data:
            old_teammates = rubric_data.get(JSON_KEY_TEAMMATES, [])
            teammates = data.get(TEAMMATES_KEY, [])

            # Déplacer le gestionnaire du répertoire
            teammate_manager = TeammateManager(rubrics_dir)
            normalized_teammates = teammate_manager.normalize_teammates(teammates)
            rubric_data[JSON_KEY_TEAMMATES] = normalized_teammates

            current_student = rubric_data.get(JSON_KEY_STUDENT, {})
            teammate_manager.sync_teammates(
                current_student=current_student,
                new_teammates=normalized_teammates,
                old_teammates=old_teammates,
            )

        # Sauvegarder le fichier
        repository.save_rubric(filename, rubric_data)

        return jsonify({"success": True, "message": "Rubric sauvegardée avec succès"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@rubrics_bp.route("/api/rubric/<filename>/copy-to-teammates", methods=["POST"])
def api_copy_to_teammates(filename):
    """Copie la grille, le commentaire et la note ajustée aux coéquipiers sélectionnés."""
    rubrics_dir = current_app.config["RUBRICS_DIR"]
    repository = RubricRepository(rubrics_dir)
    student_service = StudentService(rubrics_dir)

    if not repository.file_exists(filename):
        return jsonify({"error": "Fichier non trouvé"}), 404

    try:
        payload = request.get_json()
        teammates = payload.get(TEAMMATES_KEY, [])

        teammate_manager = TeammateManager(rubrics_dir)
        normalized_teammates = teammate_manager.normalize_teammates(teammates)

        source_data = repository.load_rubric(filename)

        current_student = source_data.get(JSON_KEY_STUDENT, {})
        current_id = (current_student.get(JSON_KEY_OMNIVOX_ID) or "").strip()
        old_teammates = source_data.get(JSON_KEY_TEAMMATES, [])
        source_data[JSON_KEY_TEAMMATES] = normalized_teammates

        # Assurer la cohérence mutuelle des coéquipiers
        teammate_manager.sync_teammates(
            current_student=current_student,
            new_teammates=normalized_teammates,
            old_teammates=old_teammates,
        )

        student_index = student_service.build_index()
        updated = []
        skipped = []

        for teammate in normalized_teammates:
            omnivox_id = (teammate.get(JSON_KEY_OMNIVOX_ID) or "").strip()
            if not omnivox_id or omnivox_id not in student_index:
                skipped.append(omnivox_id or "")
                continue

            teammate_file = student_index[omnivox_id]
            try:
                with open(teammate_file, encoding="utf-8") as tf:
                    teammate_data = json.load(tf)

                RubricSerializer.copy_grid_comment_and_grade(source_data, teammate_data)

                if current_id:
                    teammate_data[JSON_KEY_TEAMMATES] = [
                        member
                        for member in [
                            {
                                JSON_KEY_FIRSTNAME: current_student.get(JSON_KEY_FIRSTNAME, ""),
                                JSON_KEY_LASTNAME: current_student.get(JSON_KEY_LASTNAME, ""),
                                JSON_KEY_OMNIVOX_ID: current_id,
                            }
                        ]
                        + normalized_teammates
                        if (member.get(JSON_KEY_OMNIVOX_ID) or "").strip() != omnivox_id
                    ]

                with open(teammate_file, "w", encoding="utf-8") as tf:
                    json.dump(teammate_data, tf, ensure_ascii=False, indent=2)

                updated.append(omnivox_id)
            except Exception:
                skipped.append(omnivox_id)

        return jsonify({"success": True, "updated": updated, "skipped": skipped})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
