def validate_rubric(rubric: dict) -> None:
    """Validate that the rubric has the required structure."""
    assert_non_empty_string(rubric, "cours")
    assert_non_empty_string(rubric, "session")
    assert_non_empty_string(rubric, "évaluation")
    assert_total_points(rubric)
    validate_descriptors(rubric)


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