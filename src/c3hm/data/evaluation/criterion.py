from decimal import Decimal
from typing import Self

from pydantic import BaseModel, Field, model_validator

from c3hm.data.evaluation.indicator import Indicator
from c3hm.utils.decimal import decimal_to_number
from c3hm.utils.excel import safe_for_named_cell


class Criterion(BaseModel):
    """
    Représente un critère d'évaluation. Ce dernière est formée d'une liste d'indicateurs.
    """
    id: str = Field(..., min_length=1, description="Identifiant unique du critère.")
    name: str = Field(..., min_length=1)
    indicators: list[Indicator] = Field(..., min_length=1)
    override_grade: Decimal | None = Field(..., ge=Decimal(0))
    comment: str

    @property
    def has_grade(self) -> bool:
        """
        Indique si le critère est noté.
        """
        return self.override_grade is not None or self.indicators[0].has_grade

    @property
    def has_override(self) -> bool:
        """
        Indique si une note de critère a été définie manuellement.
        """
        return self.override_grade is not None

    def get_grade(self) -> Decimal:
        """
        Retourne la note du critère, en tenant compte de l'override si présent.
        """
        if not self.has_grade:
            raise ValueError(
                "Le critère n'est pas noté. Aucune note n'est définie pour le critère."
            )
        if self.override_grade is None:
            return sum((indicator.grade for indicator in self.indicators), # type: ignore
                       start=Decimal(0))
        else:
            return self.override_grade


    @model_validator(mode="after")
    def validate_indicator(self) -> Self:
        # Valide que le critère est correctement défini.
        if not safe_for_named_cell(self.id):
            raise ValueError(f"L'identifiant '{self.id}' n'est pas valide pour une cellule Excel.")

        # Vérifie que les points des indicateurs sont des multiples du pas de notation
        if self.override_grade:
            # Tous les indicateurs doivent être notés
            if not all(indicator.has_grade for indicator in self.indicators):
                raise ValueError(
                    "Tous les indicateurs du critère doivent être notés si une note manuelle"
                    " est définie."
                )
            if self.override_grade > self.points:
                raise ValueError(
                    f"La valeur de la note manuelle ({self.override_grade}) ne peut pas dépasser "
                    f"le nombre de points attribués au critère ({self.points})."
                )
        else:
            # Soit tous les indicateurs sont notés, soit aucun
            if (any(indicator.has_grade for indicator in self.indicators) and
                not all(indicator.has_grade for indicator in self.indicators)):
                raise ValueError(
                    "Tous les indicateurs du critère doivent être notés ou aucun ne doit l'être "
                )
        # Id unique pour les indicateurs
        ids = {}
        for indicator in self.indicators:
            ids[indicator.id] = ids.get(indicator.id, 0) + 1
        if len(ids) != len(self.indicators):
            dups = [id_ for id_, count in ids.items() if count > 1]
            raise ValueError(
                f"Les identifiants des indicateurs du critère '{self.name}' doivent être uniques. "
                f"Les identifiants suivants sont dupliqués : {', '.join(dups)}."
            )

        # Commentaire sans espace superflu
        self.comment = self.comment.strip()

        return self

    @property
    def points(self) -> Decimal:
        """
        Retourne le nombre total de points attribués au critère, en sommant les
        points de tous les indicateurs.
        """
        return sum((indicator.points for indicator in self.indicators),
                   start=Decimal(0))

    @property
    def nb_indicators(self) -> int:
        """
        Retourne le nombre d'indicateurs dans le critère.
        """
        return len(self.indicators)

    def to_dict(self, convert_decimal: bool = False) -> dict:
        """
        Retourne un dictionnaire représentant le critère.
        """
        if self.override_grade is not None:
            grade = (decimal_to_number(self.override_grade)
                     if convert_decimal else self.override_grade)
        else:
            grade = None
        return {
            "id": self.id,
            "nom": self.name,
            "indicateurs": [indicator.to_dict(convert_decimal=convert_decimal)
                            for indicator in self.indicators],
            "note manuelle": grade,
            "commentaire": self.comment,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Criterion":
        """
        Crée une instance de Criterion à partir d'un dictionnaire.
        """
        return cls(
            id=data["id"],
            name=data["nom"],
            indicators=[Indicator.from_dict(ind) for ind in data["indicateurs"]],
            override_grade=data.get("note manuelle"),
            comment=data.get("commentaire", ""),
        )

    def copy(self) -> "Criterion": # type: ignore
        """
        Retourne une copie du critère.
        """
        return Criterion(
            id=self.id,
            name=self.name,
            indicators=[indicator.copy() for indicator in self.indicators],
            override_grade=self.override_grade,
            comment=self.comment
        )
