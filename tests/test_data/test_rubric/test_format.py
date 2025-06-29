import pytest
from pydantic import ValidationError

from c3hm.data.rubric.format import Format


def test_format_valid_creation():
    fmt = Format(
        orientation="portrait",
        show_indicators_percent=True,
        columns_width=[10.0, 20.5, None],
        columns_width_comments=[15.0, None]
    )
    assert fmt.orientation == "portrait"
    assert fmt.show_indicators_percent is True
    assert fmt.columns_width == [10.0, 20.5, None]
    assert fmt.columns_width_comments == [15.0, None]

def test_format_default_values():
    fmt = Format()
    assert fmt.orientation is None
    assert fmt.show_indicators_percent is False
    assert fmt.columns_width == []
    assert fmt.columns_width_comments == []

def test_format_to_dict():
    fmt = Format(
        orientation="paysage",
        show_indicators_percent=True,
        columns_width=[12.0, None],
        columns_width_comments=[8.0]
    )
    d = fmt.to_dict()
    assert d["orientation"] == "paysage"
    assert d["afficher le pourcentage des indicateurs"] is True
    assert d["largeur des colonnes"] == [12.0, None]
    assert d["largeur des colonnes avec commentaires"] == [8.0]

def test_format_from_dict():
    d = {
        "orientation": "portrait",
        "afficher le pourcentage des indicateurs": False,
        "largeur des colonnes": [5.0, 10.0],
        "largeur des colonnes avec commentaires": [7.0]
    }
    fmt = Format.from_dict(d)
    assert fmt.orientation == "portrait"
    assert fmt.show_indicators_percent is False
    assert fmt.columns_width == [5.0, 10.0]
    assert fmt.columns_width_comments == [7.0]

def test_format_from_dict_missing_keys():
    d = {}
    fmt = Format.from_dict(d)
    assert fmt.orientation is None
    assert fmt.show_indicators_percent is False
    assert fmt.columns_width == []
    assert fmt.columns_width_comments == []

def test_format_copy():
    fmt = Format(
        orientation="paysage",
        show_indicators_percent=True,
        columns_width=[1.0, 2.0],
        columns_width_comments=[3.0]
    )
    fmt_copy = fmt.copy()
    assert fmt_copy == fmt
    assert fmt_copy is not fmt
    assert fmt_copy.columns_width is not fmt.columns_width
    assert fmt_copy.columns_width_comments is not fmt.columns_width_comments

def test_format_invalid_orientation():
    with pytest.raises(ValidationError):
        Format(orientation="invalid") # type: ignore
