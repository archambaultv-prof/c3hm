from decimal import Decimal

from c3hm.utils import is_multiple_of_quantum, split_decimal


def test_is_multiple_of_quantum():
    """
    Teste la fonction has_max_decimals pour vérifier le nombre de décimales.
    """
    assert is_multiple_of_quantum(Decimal("123.456"), Decimal("0.001")) is True
    assert is_multiple_of_quantum(Decimal("123.4567"), Decimal("0.001")) is False
    assert is_multiple_of_quantum(Decimal("123.4"), Decimal("0.1")) is True
    assert is_multiple_of_quantum(Decimal("123"), Decimal("1")) is True


def test_split_decimal():
    """
    Teste la fonction split_decimal pour vérifier la répartition des décimales.
    """
    x = Decimal("3.98")
    nb_of_parts = 4
    precision = Decimal("0.01")
    parts = split_decimal(x, nb_of_parts, precision)
    assert len(parts) == nb_of_parts
    assert sum(parts) == x
    assert parts == [Decimal("1.00"), Decimal("1.00"), Decimal("0.99"), Decimal("0.99")]

    x = Decimal("3.98")
    nb_of_parts = 4
    precision = Decimal("0.02")
    parts = split_decimal(x, nb_of_parts, precision)
    assert len(parts) == nb_of_parts
    assert sum(parts) == x
    assert parts == [Decimal("1.00"), Decimal("1.00"), Decimal("1.00"), Decimal("0.98")]
