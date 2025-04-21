from c3hm.core.rubric import Rubric, load_rubric_from_xlsx


def test_load_rubric_5(rubric_5_path):
    rubric = load_rubric_from_xlsx(rubric_5_path)
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

    # Vérifiez les critères et indicateurs
    cs = rubric.grid.criteria
    assert len(cs) == 3
    for i in range(3):
        assert cs[i].name == f"C{i+1}"
        assert len(cs[i].indicators) == 3
        for j in range(3):
            assert cs[i].indicators[j].name == f"C{i+1}_I{j+1}"
            assert len(cs[i].indicators[j].descriptors) == 5
            for k in range(5):
                assert cs[i].indicators[j].descriptors[k] == f"C{i+1}_I{j+1}_D{k+1}"
