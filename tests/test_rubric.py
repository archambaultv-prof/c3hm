from c3hm.core.rubric import Rubric, load_rubric_from_xlsx


def test_load_rubric_5(rubric_template_5_path):
    rubric = load_rubric_from_xlsx(rubric_template_5_path)
    assert rubric is not None
    assert isinstance(rubric, Rubric)

    # Vérifiez les propriétés principales
    assert rubric.course == "420-TEST-MA"
    assert rubric.evaluation == "TP1"

    # Vérifiez barème et seuils
    assert rubric.grid.scale == ["Excellent", "Très bien", "Bien", "Passable", "Insuffisant"]
    assert rubric.grid.total_score == 100
    assert rubric.grid.pts_precision == 0
    assert rubric.grid.thresholds == [100, 85, 70, 60, 0]
    assert rubric.grid.thresholds_precision == 0

    # Vérifiez les critères et indicateurs
    cs = rubric.grid.criteria
    assert len(cs) == 2
