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
