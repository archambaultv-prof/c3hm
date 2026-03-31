"""
Constantes pour les clés JSON du domaine de données (rubrics, étudiants, etc.).

Ces clés sont utilisées partout dans le module data et persistent dans les fichiers JSON.
"""

# Rubric structure keys
JSON_KEY_GRID = "grille"
JSON_KEY_CRITERIA = "critères"
JSON_KEY_INDICATORS = "indicateurs"
JSON_KEY_GRADED_LEVEL = "niveau noté"
JSON_KEY_GRADE_OVERRIDE = "note ajustée"
JSON_KEY_STUDENT = "étudiant"
JSON_KEY_COMMENT = "commentaire"
JSON_KEY_TEAMMATES = "coéquipiers"

# Student data keys
JSON_KEY_FIRSTNAME = "prénom"
JSON_KEY_LASTNAME = "nom"
JSON_KEY_OMNIVOX_ID = "matricule"
JSON_KEY_STUDENT_TEAM = "équipe"
JSON_KEY_TEAM_REFERENCE = "référence d'équipe"

# Rubric-level keys
JSON_KEY_COURSE = "cours"
JSON_KEY_SESSION = "session"
JSON_KEY_EVALUATION = "évaluation"

# Criterion-level keys
JSON_KEY_CRITERION_LABEL = "critère"

# Indicator-level keys
JSON_KEY_INDICATOR_LABEL = "indicateur"
JSON_KEY_POINTS = "points"
JSON_KEY_DESCRIPTORS = "descripteurs"

# Grid display keys
JSON_KEY_LEVELS = "niveaux"
JSON_KEY_SHOW_CRITERIA_POINTS = "afficher les points des critères"
JSON_KEY_SHOW_LEVELS_PERCENTAGE = "afficher les pourcentages des niveaux"
