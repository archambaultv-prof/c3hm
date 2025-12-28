from c3hm.data.student import Student, find_student_by_name

DEFAULT_DESCRIPTORS = [
    "Entièrement conforme aux attentes.",
    "Globalement conforme aux attentes : quelques éléments perfectibles.",
    "Partiellement conforme aux attentes : une erreur significative.",
    "Faiblement conforme aux attentes : erreurs significatives, erreur grave ou démarche inadéquate.",
    "Non conforme aux attentes."
]



def is_single_student_rubric(rubric: dict) -> bool:
    """Détermine si la grille d'évaluation est pour un étudiant individuel."""
    return "étudiant" in rubric

def validate_student(s: dict, student_list: list[Student] | None) -> None:
    if "étudiant" not in s:
        raise ValueError("La grille de l'étudiant doit contenir une section 'étudiant'.")
    student = s["étudiant"]
    if "nom" not in student or not isinstance(student["nom"], str) or student["nom"].strip() == "":
        raise ValueError("Le champ 'nom' de l'étudiant doit être une chaîne de caractères non vide.")
    if "matricule" not in student:
        if not student_list:
            raise ValueError("Le fichier d'étudiants doit être fourni pour faire la correspondance par nom.")
        s1 = find_student_by_name(student["nom"], student_list)
        s["étudiant"]["matricule"] = s1.omnivox_id
        s["étudiant"]["nom"] = s1.full_name()

def validate_rubric(rubric: dict) -> None:
    """Validate that the rubric has the required structure."""
    assert_non_empty_string(rubric, "cours")
    assert_non_empty_string(rubric, "session")
    assert_non_empty_string(rubric, "évaluation")
    assert_total_points(rubric)
    validate_descriptors(rubric)

    if is_single_student_rubric(rubric):
        assert_non_empty_string(rubric["étudiant"], "nom")
        assert_non_empty_string(rubric["étudiant"], "matricule")
        none_if_missing_or_empty(rubric, "commentaire")
        for item in rubric.get("critères", []):
            none_if_missing_or_empty(item, "commentaire")

def none_if_missing_or_empty(d: dict, field_name: str) -> None:
    if field_name not in d:
        d[field_name] = None
        return
    value = d[field_name]
    if isinstance(value, str):
        if value.strip() == "":
            d[field_name] = None
    elif value is None:
        return
    else:
        raise ValueError(f"Le champ '{field_name}' doit être une chaîne de caractères.")

def assert_non_empty_string(d: dict, field_name: str) -> None:
    value = d.get(field_name)
    if value is None or not isinstance(value, str) or value.strip() == "":
        raise ValueError(f"Le champ '{field_name}' doit être une chaîne de caractères non vide.")

def assert_total_points(rubric: dict) -> None:
    total_points = 0.0
    for node in rubric.get("critères", []):
        if "critère" in node:
            if "points" not in node:
                raise ValueError(f"Le critère '{node['critère']}' doit contenir un champ 'points'.")
            points = node["points"]
            if not isinstance(points, int | float) or points < 0:
                raise ValueError(f"Le champ 'points' doit être un nombre positif. Valeur trouvée: {points}")
            total_points += points
    if round(total_points, 2) != 100:
        raise ValueError(f"La somme totale des points des critères doit être égale à 100. Total trouvé: {total_points}")

def validate_descriptors(rubric: dict) -> None:
    for node in rubric.get("critères", []):
        if "critère" in node and "descripteurs" in node:
            descripteurs = node["descripteurs"]
            if not isinstance(descripteurs, list) or len(descripteurs) != 5:
                raise ValueError(f"Le critère '{node['critère']}' doit contenir une liste de 5 descripteurs.")
            for desc in descripteurs:
                if not isinstance(desc, str) or desc.strip() == "":
                    raise ValueError(f"Chaque descripteur du critère '{node['critère']}' doit être une chaîne de caractères non vide.")

def process_single_student_rubric(rubric: dict) -> dict:
    """
    Calcule différentes valeurs pour un étudiant à partir de la grille de correction.
    """
    grade = 0.0
    for node in rubric["critères"]:
        if "section" in node:
            continue
        if "pourcentage" not in node:
            raise ValueError("Chaque critère doit contenir un pourcentage.")
        node["pourcentage"] = parse_percent(node["pourcentage"])
        node["note"] = round(node["pourcentage"] * node["points"], 1)
        grade += node["note"]
    bonus_malus = rubric.get("bonus malus", {})
    if bonus_malus.get("points") is not None:
        grade += bonus_malus["points"]
    rubric["note"] = round(grade, 0)
    if "commentaire" in rubric and rubric["commentaire"] is not None and rubric["commentaire"].strip():
        rubric["commentaire"] = rubric["commentaire"].strip()
    elif rubric["note"] >= 90:
        rubric["commentaire"] = "Très bon travail!"
    else:
        rubric["commentaire"] = None
    return rubric


def parse_percent(note: str | float | int | None) -> float:
    if note is None:
        raise ValueError("La note ne peut pas être None")
    if isinstance(note, float | int):
        grade = float(note)
    elif isinstance(note, str):
        note = note.strip().lower()
        if note in ("tb", "très bien", "tres bien"):
            grade =  1.0
        elif note in ("b", "bien"):
            grade =  0.80
        elif note in ("p", "passable"):
            grade =  0.6
        elif note in ("a", "à améliorer", "a ameliorer"):
            grade =  0.30
        elif note in ("i", "insuffisant"):
            grade =  0.0
        else:
            grade =  float(note)
    else:
        raise TypeError(f"Type de note inattendu: {type(note)}")
    if not (0.0 <= grade <= 1.0):
        raise ValueError(f"La note doit être entre 0 et 1. Valeur reçue: {note}")
    return grade
