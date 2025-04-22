from decimal import Decimal

from c3hm.core.utils import has_max_decimals, split_decimal


def test_has_max_decimals():
    """
    Teste la fonction has_max_decimals pour vérifier le nombre de décimales.
    """
    assert has_max_decimals(Decimal("123.456"), 3) is True
    assert has_max_decimals(Decimal("123.4567"), 3) is False
    assert has_max_decimals(Decimal("123.4"), 3) is True
    assert has_max_decimals(Decimal("123"), 3) is True


def test_split_decimal():
    """
    Teste la fonction split_decimal pour vérifier la répartition des décimales.
    """
    x = Decimal("3.98")
    nb_of_parts = 4
    max_places = 2
    parts = split_decimal(x, nb_of_parts, max_places)
    assert len(parts) == nb_of_parts
    assert sum(parts) == x
    assert parts == [Decimal("1.00"), Decimal("1.00"), Decimal("0.99"), Decimal("0.99")]
