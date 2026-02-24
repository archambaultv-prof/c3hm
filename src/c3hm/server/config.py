"""
Configuration et constantes pour le serveur Flask (API).

Les clés JSON du domaine (French keys) sont définies dans c3hm.data.constants
et réexportées depuis c3hm.data.

Ce module contient uniquement:
- Le sentinel UNSET pour la logique serveur
- Les clés de payload API (English names) qui viennent du frontend JavaScript
"""


class UnsetType:
    """Sentinel type pour indiquer une valeur non définie."""

    pass


# Sentinel utilisé pour distinguer "une valeur n'a pas été fournie" de "une valeur est None"
UNSET = UnsetType()

# API payload keys (English) - these come from the frontend JavaScript
CRITERIA_OVERRIDE_KEY = "criteria_overrides"
RUBRIC_OVERRIDE_KEY = "rubric_grade_override"
TEAMMATES_KEY = "teammates"
COMMENT_KEY = "comment"
