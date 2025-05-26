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


def is_multiple_of_quantum(x: Decimal, quantum: Decimal) -> bool:
    """
    Retourne True si x est un multiple exact de quantum,
    c’est-à-dire que x % quantum == 0.
    """
    if quantum <= 0:
        raise ValueError("quantum must be positive")
    return (x % quantum) == 0

def split_decimal(
    x: Decimal,
    nb_of_parts: int,
    quantum: Decimal
) -> list[Decimal]:
    """
    Fractionne x en nb_of_parts parts telles que :
      - elles totalisent exactement x,
      - les nb_of_parts-1 premières sont des multiples de quantum,
      - elles diffèrent d'au plus une unité de quantum

    Lance une exception si x n'est pas un multiple exact de quantum.
    """
    # Vérification x et quantum
    if not is_multiple_of_quantum(x, quantum):
        raise ValueError(f"{x!r} n'est pas un multiple exact de {quantum!r}")

    # Nombre de quanta entiers dans x
    total_units = int((x // quantum).to_integral_value())

    # Répartition des unités entières
    units_list = split_integer(total_units, nb_of_parts)

    # Conversion en Decimal
    parts = [Decimal(u) * quantum for u in units_list]

    return parts



def round_to_nearest_quantum(x: Decimal, quantum: Decimal) -> Decimal:
    """
    Arrondit x au multiple de quantum le plus proche.
    Si x est exactement à mi-chemin entre deux multiples de quantum,
    arrondit vers le multiple supérieur.
    """
    if quantum <= 0:
        raise ValueError("quantum doit être positif")
    return (x / quantum).to_integral_value(rounding=ROUND_HALF_UP) * quantum


def decimal_to_number(d: Decimal) -> float | int:
    """
    Convertit un nombre décimal en nombre flottant
    ou entier, selon la valeur.
    """
    if d == d.to_integral_value():
        return int(d)
    else:
        return float(d)
