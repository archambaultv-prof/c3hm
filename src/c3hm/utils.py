from decimal import ROUND_HALF_UP, Decimal


def split_integer(n: int, nb_of_parts: int) -> list[int]:
    """
    Divise un entier n en nb_of_parts parties entières aussi égales que possible.

    Chaque partie est un entier, et la somme des nb_of_parts parties est exactement égale à n.
    Si la division n'est pas exacte, les premières parties recevront une unité de plus.

    Par exemple :
    - split_integer(10, 3) retourne [4, 3, 3]
    - split_integer(-7, 4) retourne [-1, -2, -2, -2]

    Paramètres :
    - n (int) : l'entier à diviser
    - nb_of_parts (int) : le nombre de parties

    Retour :
    - list[int] : une liste de nb_of_parts entiers dont la somme est n
    """
    base = n // nb_of_parts
    remainder = n % nb_of_parts
    return [base + 1] * remainder + [base] * (nb_of_parts - remainder)


def is_within_decimal_limit(d: Decimal, max_places: int) -> bool:
    """
    Vérifie si le nombre décimal a au plus max_places décimales.
    """
    t = d.normalize().as_tuple()
    places = -t.exponent if t.exponent < 0 else 0
    return places <= max_places


def split_decimal(
    x: Decimal,
    nb_of_parts: int,
    max_places: int
) -> list[Decimal]:
    """
    Fractionne X en N parts qui :
      - totalisent exactement X,
      - ont au plus max_places décimales,
      - diffèrent d’au plus une unité de quantum (10⁻max_places).
    """
    # 1) Construire le facteur et le quantum (plus petite unité)
    factor  = Decimal(10) ** max_places       # ex. max_places=2 → factor=100
    quantum = Decimal(1) / factor             # ex. Decimal('0.01')

    # 2) Arrondir X à la précision désirée
    xq = x.quantize(quantum, rounding=ROUND_HALF_UP)

    # 3) Convertir Xq en nombre entier de quanta
    xq_int = int((xq * factor).to_integral_value())

    # 4) Appeler la fonction split_integer pour diviser l'entier
    xs = split_integer(xq_int, nb_of_parts)

    # 5) Reconvertir les parties en décimales
    parts = [Decimal(i) / factor for i in xs]

    return parts


def decimal_is_integer(d: Decimal) -> bool:
    """
    Vérifie si le nombre décimal est un entier.
    """
    return d == d.to_integral_value()


def decimal_to_number(d: Decimal) -> float | int:
    """
    Convertit un nombre décimal en nombre flottant
    ou entier, selon la valeur.
    """
    if decimal_is_integer(d):
        return int(d)
    else:
        return float(d)
