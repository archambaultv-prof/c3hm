from c3hm.core.rubric import Rubric, load_rubric_from_yaml


def test_load_rubric_1(rubric_1_path):
    rubric = load_rubric_from_yaml(rubric_1_path)
    assert rubric is not None
    assert isinstance(rubric, Rubric)

    # Vérifiez les propriétés principales
    assert rubric.course == "420-TEST-MA"
    assert rubric.evaluation == "TP1"

    # Vérifiez barème et seuils
    assert rubric.grid.scale == ["A", "B", "C", "D", "E"]
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


def test_load_rubric_minimal(rubric_minimal_path):
    rubric = load_rubric_from_yaml(rubric_minimal_path)
    assert rubric is not None
    assert isinstance(rubric, Rubric)

    # Vérifiez les propriétés principales
    assert rubric.course is None
    assert rubric.evaluation is None
    assert rubric.title() == "Grille d'évaluation"

    # Vérifiez barème et seuils
    assert rubric.grid.scale == ["Excellent", "Très bien", "Bien", "Passable", "Insuffisant"]
    assert rubric.grid.thresholds == [100, 85, 70, 60, 0]

    # Vérifiez les critères et indicateurs
    cs = rubric.grid.criteria
    assert len(cs) == 1
    assert cs[0].name == "C1"
    assert len(cs[0].indicators) == 1
    assert cs[0].indicators[0].name == "C1_I1"
    assert len(cs[0].indicators[0].descriptors) == 5
    for k in range(5):
        assert cs[0].indicators[0].descriptors[k] == f"C1_I1_D{k+1}"
