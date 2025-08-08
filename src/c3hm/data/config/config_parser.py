from decimal import Decimal
from pathlib import Path

import c3hm.data.user_config.config_parser as ucp
from c3hm.data.config.config import Config
from c3hm.data.config.criterion import Criterion
from c3hm.data.config.evaluation import Evaluation
from c3hm.data.config.grade_level import GradeLevel
from c3hm.data.config.indicator import Indicator
from c3hm.data.user_config.config import UserConfig
from c3hm.data.user_config.criterion import UserCriterion
from c3hm.data.user_config.evaluation import UserEvaluation
from c3hm.utils.decimal import split_decimal


def config_from_yaml(yaml_path: Path | str) -> Config:
        """
        Charge la configuration à partir d'un fichier YAML.
        """
        c = ucp.config_from_yaml(yaml_path)
        return from_user_config(c)

def from_user_config(user_config: UserConfig) -> Config:
    """
    Charge la configuration à partir d'une configuration utilisateur.
    """
    eval = from_user_eval(user_config.evaluation)
    return Config(evaluation=eval, format=user_config.format,
                  students=user_config.students)

def from_user_eval(user_eval: UserEvaluation) -> Evaluation:
    """
    Convertit une évaluation utilisateur en une instance d'évaluation.
    """
    # Update a copy of the user evaluation to avoid modifying the original
    # The recast this validated copy to a new Evaluation instance
    user_eval = user_eval.model_copy(deep=True)
    _check_grade_levels(user_eval.grade_levels)
    _check_descriptors(user_eval)
    _infer_ids(user_eval)
    _infer_pts(user_eval)

    return _from_user_eval(user_eval)

def _from_user_eval(user_eval: UserEvaluation) -> Evaluation:
    criteria = []
    for c in user_eval.criteria:
        indicators = []
        for i in c.indicators:
            indicators.append(Indicator(name=i.name, excel_id=i.excel_id, # type: ignore
                                       descriptors=i.descriptors,
                                       points=i.points)) # type: ignore
        criteria.append(Criterion(name=c.name, excel_id=c.excel_id, # type: ignore
                                points_total=c.points_total, indicators=indicators)) # type: ignore
    return Evaluation(
        criteria=criteria,
        name=user_eval.name,
        points_inference_step=user_eval.points_inference_step,
        points_total=user_eval.points_total, # type: ignore
        points_total_nb_of_decimal=user_eval.points_total_nb_of_decimal,
        grade_levels=user_eval.grade_levels)


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

def _check_descriptors(user_eval: UserEvaluation) -> None:
    """
    Vérifie que les descripteurs des critères sont valides.
    """
    nb_levels = len(user_eval.grade_levels)
    for criterion in user_eval.criteria:
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

def _infer_ids(user_eval: UserEvaluation):
    """
    Infère les identifiants des critères et des indicateurs.
    """
    seen = set([user_eval.excel_id])
    for idx_c, criterion in enumerate(user_eval.criteria):
        if criterion.excel_id is None:
            criterion.excel_id = f"C{idx_c + 1}"
        else:
            if criterion.excel_id in seen:
                raise ValueError(f"Identifiant de critère '{criterion.excel_id}' déjà utilisé.")
        seen.add(criterion.excel_id)
        for idx_i, indicator in enumerate(criterion.indicators):
            if indicator.excel_id is None:
                indicator.excel_id = f"C{idx_c + 1}_I{idx_i + 1}"
            else:
                if indicator.excel_id in seen:
                    raise ValueError(f"Identifiant d'indicateur '{indicator.excel_id}'"
                                     "déjà utilisé.")
            seen.add(indicator.excel_id)
    return user_eval

def _infer_pts(user_eval: UserEvaluation):
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
        for criterion in user_eval.criteria:
            progress = _infer_criterion_indicators_pts(criterion, user_eval) or progress
        progress = _infer_eval_criteria_pts(user_eval) or progress
        if not progress:
            break

    # Vérifie que tous les points totaux sont définis, car il existe des cas où
    # l'inférence n'est pas possible.
    if user_eval.points_total is None:
        raise ValueError("Le total des points de l'évaluation ne peut pas être inféré.")
    for criterion in user_eval.criteria:
        if criterion.points_total is None:
            raise ValueError(f"Le total des points du critère '{criterion.name}'"
                             "ne peut pas être inféré.")
        for indicator in criterion.indicators:
            if indicator.points is None:
                raise ValueError(f"Le point de l'indicateur '{indicator.name}' du critère "
                                 f"'{criterion.name}' ne peut pas être inféré.")


def _infer_criterion_indicators_pts(criterion: UserCriterion, user_eval: UserEvaluation) -> bool:
    progress = False
    if criterion.points_total is None:
        # On essaie de calculer le total à partir des points des indicateurs
        total = Decimal("0")
        for indicator in criterion.indicators:
            if indicator.points is None:
                total = None
                break
            total += indicator.points
        if total is not None:
            criterion.points_total = total
            progress = True
    else:
        # On essaie de calculer les points des indicateurs à partir du total du critère
        pts_indicators = sum((i.points for i in criterion.indicators if i.points is not None),
                             start=Decimal("0"))
        if pts_indicators > criterion.points_total:
            raise ValueError(f"Le total des points des indicateurs ({pts_indicators}) "
                             f"dépasse le total du critère ({criterion.points_total}).")
        elif pts_indicators < criterion.points_total:
            ind_without_pts = [i for i in criterion.indicators if i.points is None]
            if not ind_without_pts:
                raise ValueError(f"Le total des points des indicateurs ({pts_indicators}) "
                                 f"est inférieur au total du critère ({criterion.points_total}). "
                                 "Aucun indicateur sans points définis pour ajuster.")
            # On répartit les points restants sur les indicateurs sans points définis
            remaining_points = split_decimal(criterion.points_total - pts_indicators,
                                             len(ind_without_pts),
                                             user_eval.points_inference_step)
            for indicator, points in zip(ind_without_pts, remaining_points, strict=True):
                indicator.points = points
            progress = True

    return progress

def _infer_eval_criteria_pts(user_eval: UserEvaluation) -> bool:
    """
    Infère les points totaux des critères de l'évaluation.
    """
    progress = False
    if user_eval.points_total is None:
        # On essaie de calculer le total à partir des points des critères
        total = Decimal("0")
        for criterion in user_eval.criteria:
            if criterion.points_total is None:
                total = None
                break
            total += criterion.points_total
        if total is not None:
            user_eval.points_total = total
            progress = True
    else:
        # On essaie de calculer les points des critères à partir du total de l'évaluation
        pts_criteria = sum((criterion.points_total for criterion in user_eval.criteria
                            if criterion.points_total is not None),
                           start=Decimal("0"))
        if pts_criteria > user_eval.points_total:
            raise ValueError(f"Le total des points des critères ({pts_criteria}) "
                             f"dépasse le total de l'évaluation ({user_eval.points_total}).")
        elif pts_criteria < user_eval.points_total:
            criteria_without_pts = [c for c in user_eval.criteria if c.points_total is None]
            if not criteria_without_pts:
                raise ValueError(f"Le total des points des critères ({pts_criteria}) "
                                 "est inférieur au total de "
                                 f"l'évaluation ({user_eval.points_total})."
                                 "Aucun critère sans points définis pour ajuster.")
            # On répartit les points restants sur les critères sans points définis
            remaining_points = split_decimal(user_eval.points_total - pts_criteria,
                                             len(criteria_without_pts),
                                             user_eval.points_inference_step)
            for criterion, points in zip(criteria_without_pts, remaining_points, strict=True):
                criterion.points_total = points
            progress = True

    return progress
