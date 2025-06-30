from pathlib import Path

from c3hm.data.config import Config
from c3hm.data.rubric.format import Format
from c3hm.data.student.student import Student


def make_student(first_name="Alice", last_name="Smith", alias="alice", omnivox_code="12345"):
    return Student(first_name=first_name, last_name=last_name, alias=alias,
                   omnivox_code=omnivox_code)

def make_rubric_dict():
    return {
        "format": {
            "orientation": "portrait",
            "afficher le pourcentage des indicateurs": True,
            "largeur des colonnes": [10.0, 20.5, None],
            "largeur des colonnes avec commentaires": [10.0, 20.5, 15, None]
        },
        "niveaux": [
            {"nom": "Excellent", "maximum": 100, "minimum": 80},
            {"nom": "Bon", "maximum": 79, "minimum": 60},
        ],
        "évaluation": {
            "nom": "Évaluation test",
            "total": 40,
            "précision du total": 0,
            "pas pour inférence des points": 1,
            "critères": [
                {
                    "id": "C1",
                    "critère": "Critère 1",
                    "total": 30,
                    "indicateurs": [
                        {
                            "id": "C1_I1",
                            "indicateur": "Indicateur 1",
                            "points": 20,
                            "descripteurs": ["desc1", "desc2"],
                        },
                        {
                            "id": "C1_I2",
                            "indicateur": "Indicateur 2",
                            "points": 10,
                            "descripteurs": ["desc3", "desc4"],
                        }
                    ],
                },
                {
                    "id": "C2",
                    "critère": "Critère 2",
                    "total": 10,
                    "indicateurs": [
                        {
                            "id": "C2_I1",
                            "indicateur": "Indicateur 3",
                            "points": 5,
                            "descripteurs": ["desc5", "desc6"],
                        },
                        {
                            "id": "C2_I2",
                            "indicateur": "Indicateur 4",
                            "points": 5,
                            "descripteurs": ["desc7", "desc8"],
                        }
                    ],
                }
            ],
        },
    }

def make_students_list():
    return [
        {"nom de famille": "Alice", "prénom": "Smith", "alias": "alice",
         "code omnivox": "12345"},
        {"nom de famille": "Bob", "prénom": "Jones", "alias": "bob",
         "code omnivox": "67890"},
    ]

def make_config_user_dict():
    return {
        "grille": make_rubric_dict(),
        "étudiants": make_students_list(),
    }

def test_config_to_dict_and_from_dict():
    config = Config.from_user_dict(
        make_config_user_dict(),
        path=None
    )
    d = config.to_dict()
    assert "grille" in d
    assert "étudiants" in d
    config2 = Config.from_dict(d)
    assert config2 == config

def test_config_no_format():
    d = make_config_user_dict()
    del d["grille"]["format"]
    config = Config.from_user_dict(d, path=None)
    assert config.rubric.format == Format()

def test_config_no_indicators_points():
    d = make_config_user_dict()
    for criterion in d["grille"]["évaluation"]["critères"]:
        for indicator in criterion["indicateurs"]:
            del indicator["points"]
    config = Config.from_user_dict(d, path=None)
    assert config.rubric.evaluation.criteria[0].indicators[0].points == 15
    assert config.rubric.evaluation.criteria[0].indicators[1].points == 15
    assert config.rubric.evaluation.criteria[1].indicators[0].points == 5
    assert config.rubric.evaluation.criteria[1].indicators[1].points == 5

def test_config_no_indicators_points2():
    d = make_config_user_dict()
    del d["grille"]["évaluation"]["critères"][0]["indicateurs"][0]["points"]
    config = Config.from_user_dict(d, path=None)
    assert config.rubric.evaluation.criteria[0].indicators[0].points == 20
    assert config.rubric.evaluation.criteria[0].indicators[1].points == 10
    assert config.rubric.evaluation.criteria[1].indicators[0].points == 5
    assert config.rubric.evaluation.criteria[1].indicators[1].points == 5

def test_config_only_total_points():
    d = make_config_user_dict()
    for criterion in d["grille"]["évaluation"]["critères"]:
        for indicator in criterion["indicateurs"]:
            del indicator["points"]
        del criterion["total"]
    config = Config.from_user_dict(d, path=None)
    assert config.rubric.evaluation.criteria[0].indicators[0].points == 10
    assert config.rubric.evaluation.criteria[0].indicators[1].points == 10
    assert config.rubric.evaluation.criteria[1].indicators[0].points == 10
    assert config.rubric.evaluation.criteria[1].indicators[1].points == 10

def test_config_some_points():
    d = make_config_user_dict()
    for i, criterion in enumerate(d["grille"]["évaluation"]["critères"]):
        if i == 0:
            del criterion["total"]
        else:
            for i2, indicator in enumerate(criterion["indicateurs"]):
                if i2 == 0:
                    del indicator["points"]
    del d["grille"]["évaluation"]["total"]
    config = Config.from_user_dict(d, path=None)
    assert config.rubric.evaluation.criteria[0].indicators[0].points == 20
    assert config.rubric.evaluation.criteria[0].indicators[1].points == 10
    assert config.rubric.evaluation.criteria[1].indicators[0].points == 5
    assert config.rubric.evaluation.criteria[1].indicators[1].points == 5

def test_config_default_descriptors2():
    d = make_config_user_dict()
    d["grille"]["évaluation"]["descripteurs par défaut"] = ["D1", "D2"]
    for criterion in d["grille"]["évaluation"]["critères"]:
        for indicator in criterion["indicateurs"]:
            del indicator["descripteurs"]
    config = Config.from_user_dict(d, path=None)
    for criterion in config.rubric.evaluation.criteria:
        for indicator in criterion.indicators:
            for i, lvl in enumerate(config.rubric.grade_levels.levels):
                assert config.rubric.descriptors.contains(indicator, lvl)
                assert config.rubric.descriptors.get_descriptor(indicator, lvl) == f"D{i+1}"

def test_config_full_template(config_full_template_path: Path):
    Config.from_user_config(config_full_template_path)
