
from pathlib import Path

import yaml

from c3hm.data.config import Config
from c3hm.data.criterion import Criterion
from c3hm.data.grade_level import GradeLevel


def parse_user_config(path: Path,
                      include_grading: bool = False,
                      check_grades: bool = False) -> Config:
    """
    Parse le fichier de configuration à l'emplacement `path` et retourne
    une instance de `Config` validée.
    """
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    config = Config(**data)
    _check_grade_levels(config.grade_levels)
    _check_descriptors(config.criteria, len(config.grade_levels))
    _round_pts(config)
    _infer_pts(config)
    if include_grading:
        _check_student_info(config)
        _infer_grades(config)
        if check_grades:
            check_all_grades(config)
    else:
        _remove_student_info_and_grades(config)
    _round_pts(config)  # Arrondit à nouveau après inférence
    return config

def check_all_grades(config: Config) -> None:
    """
    Vérifie que les notes des indicateurs, critères et de l'évaluation
    sont valides.
    """
    if config.evaluation_grade is None:
        raise ValueError("La note de l'évaluation est requise pour une évaluation notée.")
    if not (0 <= config.evaluation_grade <= config.get_total()):
        raise ValueError("La note de l'évaluation doit être entre 0 et le total des points.")
    for criterion in config.criteria:
        if criterion.grade is None:
            raise ValueError(f"La note du critère '{criterion.name}' est requise "
                             "pour une évaluation notée.")
        if not (0 <= criterion.grade <= criterion.get_total()):
            raise ValueError(f"La note du critère '{criterion.name}' doit être entre 0 "
                             f"et le total des points ({criterion.get_total()}).")
        for indicator in criterion.indicators:
            if indicator.grade is None:
                raise ValueError(f"La note de l'indicateur '{indicator.name}' du critère "
                                 f"'{criterion.name}' est requise pour une évaluation notée.")
            if not (0 <= indicator.grade <= criterion.get_total()):
                raise ValueError(f"La note de l'indicateur '{indicator.name}' du critère "
                                 f"'{criterion.name}' doit être entre 0 et le total des points "
                                 f"du critère ({criterion.get_total()}).")

def _infer_grades(config: Config) -> None:
    """
    Infère les notes des indicateurs, critères et de l'évaluation
    à partir des points dans la configuration. Trois possibilités :
    - Seulement la note de l'évaluation est définie, on l'utilise pour
      calculer les notes des critères et des indicateurs.
    - Pour un critère, la note est définie, on l'utilise pour
      calculer les notes des indicateurs de ce critère.
    - Pour un critère, la note n'est pas définie, mais les notes
      des indicateurs sont définies, on les utilise pour calculer
      la note du critère.
    """
    funcs = [_infer_grades_from_eval_total, _infer_grades_bottom_up]
    for func in funcs:
        if func(config):
            return

def _infer_grades_from_eval_total(config: Config) -> bool:
    if config.evaluation_grade is None:
        return False

    for criterion in config.criteria:
        if criterion.grade is not None:
            return False
        for indicator in criterion.indicators:
            if indicator.grade is not None:
                return False

    # Si tous les critères et indicateurs n'ont pas de note, on utilise
    # la note de l'évaluation
    ratio = config.evaluation_grade / config.get_total()
    for criterion in config.criteria:
        criterion.grade = criterion.get_total() * ratio
        for indicator in criterion.indicators:
            indicator.grade = indicator.get_total() * ratio
    return True

def _infer_grades_bottom_up(config: Config) -> bool:
    total = 0
    for criterion in config.criteria:
        if criterion.grade is None:
            # On essaie d'inférer la note du critère à partir des notes des indicateurs
            crit_total = 0
            for indicator in criterion.indicators:
                if indicator.grade is None:
                    return False
                crit_total += indicator.grade
            criterion.grade = crit_total
        else:
            nb_none = sum(1 for indicator in criterion.indicators if indicator.grade is None)
            if nb_none == 0:
                # We have both criterion and all indicators grades defined
                continue
            elif nb_none == len(criterion.indicators):
                # On a seulement la note du critère, on l'utilise pour les indicateurs
                ratio = criterion.grade / criterion.get_total()
                for indicator in criterion.indicators:
                    indicator.grade = indicator.get_total() * ratio
            else:
                return False
        total += criterion.grade
    if config.evaluation_grade is None:
        config.evaluation_grade = total
    return True

def _remove_student_info_and_grades(config: Config) -> None:
    """
    Supprime les informations de l'étudiant et les notes de la configuration.
    """
    config.student_first_name = None
    config.student_last_name = None
    config.student_omnivox = None
    config.evaluation_grade = None
    config.evaluation_comment = None
    for criterion in config.criteria:
        criterion.grade = None
        criterion.comment = None
        for indicator in criterion.indicators:
            indicator.grade = None
            indicator.comment = None

def _check_student_info(config: Config) -> None:
    """
    Vérifie que les informations de l'étudiant sont présentes si la configuration
    est pour une évaluation notée.
    """
    if not config.student_first_name:
        raise ValueError("Le prénom de l'étudiant est requis pour une évaluation notée.")
    if not config.student_last_name:
        raise ValueError("Le nom de famille de l'étudiant est requis pour une évaluation notée.")
    if not config.student_omnivox:
        raise ValueError("Le numéro Omnivox de l'étudiant est requis pour une évaluation notée.")

def _round_pts(config: Config) -> None:
    """
    Arrondit les points des indicateurs, critères et de l'évaluation
    au nombre de décimales spécifié dans la configuration.
    """
    ndigits = config.evaluation_total_nb_decimals
    if config.evaluation_total is not None:
        config.evaluation_total = round(config.evaluation_total, ndigits)
    if config.evaluation_grade is not None:
        config.evaluation_grade = round(config.evaluation_grade, ndigits)
    for criterion in config.criteria:
        if criterion.total is not None:
            criterion.total = round(criterion.total, ndigits + 1)
        if criterion.grade is not None:
            criterion.grade = round(criterion.grade, ndigits + 1)
        for indicator in criterion.indicators:
            if indicator.points is not None:
                indicator.points = round(indicator.points, ndigits + 1)
            if indicator.grade is not None:
                indicator.grade = round(indicator.grade, ndigits + 1)

def _check_grade_levels(grade_levels: list[GradeLevel]) -> None:
    """
    Vérifie que les niveaux de note sont valides.
    """
    # Maximum du premier doit être 100
    if grade_levels[0].maximum != 100:
        raise ValueError("Le maximum du premier niveau de note doit être 100.")

    # Minimum du dernier doit être 0
    if grade_levels[-1].minimum != 0:
        raise ValueError("Le minimum du dernier niveau de note doit être 0.")

    # Vérifie que les niveaux sont ordonnés
    for i in range(1, len(grade_levels)):
        if grade_levels[i - 1].minimum < grade_levels[i].maximum:
            raise ValueError("Les niveaux de note doivent être ordonnés par ordre décroissant.")

    # Vérifie que la valeur par défaut est entre le minimum et le maximum
    for level in grade_levels:
        if not (level.minimum <= level.default_value <= level.maximum):
            raise ValueError(f"La valeur par défaut du niveau '{level.name}' "
                             "doit être entre le minimum et le maximum.")

def _check_descriptors(criteria: list[Criterion], nb_levels: int) -> None:
    """
    Vérifie que les descripteurs des critères sont valides.
    """
    for criterion in criteria:
        for indicator in criterion.indicators:
            # Nombre de descripteurs doit correspondre au nombre de niveaux
            if len(indicator.descriptors) != nb_levels:
                raise ValueError(
                    f"Le nombre de descripteurs pour l'indicateur '{indicator.name}' "
                    f"doit être égal au nombre de niveaux ({nb_levels})."
                )
            # Au moins un descripteur doit être défini
            if not any(indicator.descriptors):
                raise ValueError(
                    f"L'indicateur '{indicator.name}' doit avoir au moins un descripteur défini."
                )

def _infer_pts(config: Config):
    """
    Infère les points totaux des critères et de l'évaluation.

    Si le total d'un critère est défini, il est utilisé pour calculer ou
    vérifier les points des indicateurs.

    Si le total de l'évaluation est défini, il est utilisé pour calculer ou
    vérifier les points des critères.

    L'algorithme fixe les points d'un critère depuis les points des indicateurs
    en priorité sur l'inférence par les points totaux de l'évaluation.
    """
    while True:
        progress = False
        for criterion in config.criteria:
            progress = _infer_criterion_indicators_pts(criterion, config) or progress
        progress = _infer_eval_criteria_pts(config) or progress
        if not progress:
            break

    # Vérifie que tous les points totaux sont définis, car il existe des cas où
    # l'inférence n'est pas possible.
    if config.evaluation_total is None:
        raise ValueError("Le total des points de l'évaluation ne peut pas être inféré.")
    for criterion in config.criteria:
        if criterion.total is None:
            raise ValueError(f"Le total des points du critère '{criterion.name}'"
                             "ne peut pas être inféré.")
        for indicator in criterion.indicators:
            if indicator.points is None:
                raise ValueError(f"Le point de l'indicateur '{indicator.name}' du critère "
                                 f"'{criterion.name}' ne peut pas être inféré.")


def _infer_criterion_indicators_pts(criterion: Criterion, config: Config) -> bool:
    progress = False
    if criterion.total is None:
        # On essaie de calculer le total à partir des points des indicateurs
        total = 0
        for indicator in criterion.indicators:
            if indicator.points is None:
                total = None
                break
            total += indicator.points
        if total is not None:
            criterion.total = total
            progress = True
    else:
        # On essaie de calculer les points des indicateurs à partir du total du critère
        pts_indicators = sum((i.points for i in criterion.indicators if i.points is not None),
                             start=0)
        if pts_indicators > criterion.total:
            raise ValueError(f"Le total des points des indicateurs ({pts_indicators}) "
                             f"dépasse le total du critère ({criterion.total}).")
        elif pts_indicators < criterion.total:
            ind_without_pts = [i for i in criterion.indicators if i.points is None]
            if not ind_without_pts:
                raise ValueError(f"Le total des points des indicateurs ({pts_indicators}) "
                                 f"est inférieur au total du critère ({criterion.total}). "
                                 "Aucun indicateur sans points définis pour ajuster.")
            # On répartit les points restants sur les indicateurs sans points définis
            remaining_points = split_float(criterion.total - pts_indicators,
                                           len(ind_without_pts),
                                           config.evaluation_total_nb_decimals + 1)
            for indicator, points in zip(ind_without_pts, remaining_points, strict=True):
                indicator.points = points
            progress = True

    return progress

def _infer_eval_criteria_pts(config: Config) -> bool:
    """
    Infère les points totaux des critères de l'évaluation.
    """
    progress = False
    if config.evaluation_total is None:
        # On essaie de calculer le total à partir des points des critères
        total = 0
        for criterion in config.criteria:
            if criterion.total is None:
                total = None
                break
            total += criterion.total
        if total is not None:
            config.evaluation_total = total
            progress = True
    else:
        # On essaie de calculer les points des critères à partir du total de l'évaluation
        pts_criteria = sum((criterion.total for criterion in config.criteria
                            if criterion.total is not None),
                           start=0)
        if pts_criteria > config.evaluation_total:
            raise ValueError(f"Le total des points des critères ({pts_criteria}) "
                             f"dépasse le total de l'évaluation ({config.evaluation_total}).")
        elif pts_criteria < config.evaluation_total:
            criteria_without_pts = [c for c in config.criteria if c.total is None]
            if not criteria_without_pts:
                raise ValueError(f"Le total des points des critères ({pts_criteria}) "
                                 "est inférieur au total de "
                                 f"l'évaluation ({config.evaluation_total})."
                                 "Aucun critère sans points définis pour ajuster.")
            # On répartit les points restants sur les critères sans points définis
            remaining_points = split_float(config.evaluation_total - pts_criteria,
                                             len(criteria_without_pts),
                                             config.evaluation_total_nb_decimals + 1)
            for criterion, points in zip(criteria_without_pts, remaining_points, strict=True):
                criterion.total = points
            progress = True

    return progress

def split_float(n: float, nb_of_parts: int, ndigits: int) -> list[float]:
    """
    Divise un flottant n en nb_of_parts parties aussi égales que possible.

    Chaque partie est arrondie à ndigits décimales, et la somme des nb_of_parts parties est
    exactement égale à n.
    Si la division n'est pas exacte, les premières parties recevront une unité de plus
    au nième chiffre décimal.

    Par exemple :
    - split_float(10.0, 3, 0) retourne [4.0, 3.0, 3.0]
    - split_float(10.0, 3, 1) retourne [3.4, 3.3, 3.3]
    - split_float(-7.0, 4, 0) retourne [-1.0, -2.0, -2.0, -2.0]
    - split_float(-7.0, 4, 1) retourne [-1.8, -1.8, -1.7, -1.7]

    Paramètres :
    - n (float) : le flottant à diviser
    - nb_of_parts (int) : le nombre de parties
    - ndigits (int) : le nombre de chiffres décimaux pour l'arrondi

    Retour :
    - list[float] : une liste de nb_of_parts flottants dont la somme est n
    """
    factor = 10 ** ndigits
    base = int(n * factor) // nb_of_parts
    remainder = int(n * factor) % nb_of_parts
    parts = [base + 1] * remainder + [base] * (nb_of_parts - remainder)
    return [p / factor for p in parts]
