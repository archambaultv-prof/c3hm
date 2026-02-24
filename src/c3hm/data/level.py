import unicodedata

from c3hm.data.utils import assert_non_empty_string


def get_colors(nb_levels: int) -> list[str]:
    """
    Génère une palette de couleurs pour les niveaux de rubrique.
    """
    if nb_levels < 1:
        raise ValueError("Le nombre de niveaux doit être au moins 1.")
    if nb_levels > 5:
        raise ValueError("Le nombre de niveaux ne peut pas dépasser 5.")

    # Couleurs de base pour les 5 niveaux
    base_colors = ["#C8FFC8", "#F0FFB0", "#FFF8C2", "#FFE4C8", "#FFC8C8"]
    match nb_levels:
        case 1:
            return [base_colors[0]]
        case 2:
            return [base_colors[0], base_colors[3]]
        case 3:
            return [base_colors[0], base_colors[1], base_colors[3]]
        case 4:
            return [base_colors[0], base_colors[1], base_colors[2], base_colors[3]]
        case _:
            return base_colors


class Level:
    def __init__(self, label: str, percentage: float, short_label: list[str] | None = None):
        self.label = label
        self.percentage = percentage
        self.short_label = short_label

    def match_label(self, label: str) -> bool:
        label = self._to_matchable(label)
        if label == self._to_matchable(self.label):
            return True
        elif self.short_label is not None:
            return any(label == self._to_matchable(short) for short in self.short_label)
        return False

    def _to_matchable(self, text: str) -> str:
        return self._remove_accents(unicodedata.normalize("NFD", text)).casefold().strip()

    def _remove_accents(self, text: str) -> str:
        return "".join(c for c in text if unicodedata.category(c) != "Mn")

    def copy(self) -> "Level":
        return Level(
            label=self.label,
            percentage=self.percentage,
            short_label=self.short_label.copy() if self.short_label else None,
        )

    def validate(self) -> None:
        assert_non_empty_string(self.label, field_name="niveau")
        if not isinstance(self.percentage, int | float) or self.percentage < 0 or self.percentage > 1:
            raise ValueError(f"Le champ 'pourcentage' du niveau '{self.label}' doit être un nombre entre 0 et 1.")
        if self.short_label is not None and (
            not isinstance(self.short_label, list)
            or not all(isinstance(s, str) and s.strip() != "" for s in self.short_label)
        ):
            raise ValueError(
                f"Le champ 'abréviations' du niveau '{self.label}' doit être une liste de chaînes de caractères "
                "non vides."
            )

    def to_dict(self) -> dict:
        d = {
            "niveau": self.label,
            "pourcentage": self.percentage,
        }
        if self.short_label is not None:
            d["abréviations"] = self.short_label
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "Level":
        label = data["niveau"]
        percentage = data["pourcentage"]
        short_label = data.get("abréviations")
        return cls(label=label, percentage=percentage, short_label=short_label)


DEFAULT_LEVELS = [
    Level(label="Bien maîtrisé", percentage=1.0, short_label=["m", "maîtrisé"]),
    Level(label="Acquis", percentage=0.75, short_label=["ac"]),
    Level(label="Ça y est presque!", percentage=0.5, short_label=["p", "presque"]),
    Level(label="En apprentissage", percentage=0.25, short_label=["ap", "apprentissage"]),
    Level(label="Non démontré", percentage=0.0, short_label=["n", "nd"]),
]
