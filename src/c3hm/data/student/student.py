from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Student(BaseModel):
    """
    Représente un étudiant avec un nom, prénom, code Omnivox et alias.
    Possibilité d'être associé à une équipe. Si l'étudiant est la référence
    pour son équipe, cela implique que la note attribuée à l'étudiant
    sera également pour les coéquipiers, sauf si une note est spécifiquement
    attribuée à un coéquipier.
    """
    model_config = ConfigDict(coerce_numbers_to_str=True)

    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)
    omnivox_code: str = Field(..., min_length=1)
    alias: str = Field(..., min_length=1)
    team: str | None = None
    is_team_reference: bool = False

    @model_validator(mode="after")
    def validate_student(self) -> Self:
        """
        Valide les champs de l'étudiant après la création de l'instance.
        """
        self.first_name = self.first_name.strip()
        self.last_name = self.last_name.strip()
        self.omnivox_code = self.omnivox_code.strip()
        self.alias = self.alias.strip()
        if any(not field for field in
               [self.first_name, self.last_name, self.omnivox_code, self.alias]):
            raise ValueError(
                f"Certains champs de l'étudiant {self.omnivox_code}"
                " sont vides ou contiennent uniquement des espaces."
            )
        if self.team is not None:
            self.team = self.team.strip()
            if self.team == "":
                self.team = None
        return self

    def has_team(self) -> bool:
        """
        Vérifie si l'étudiant est associé à une équipe.
        """
        return self.team is not None and self.team.strip() != ""

    def ws_name(self) -> str:
        """
        Retourne le nom de la feuille de calcul pour l'étudiant.
        """
        return self.alias

    def to_dict(self) -> dict:
        """
        Retourne un dictionnaire représentant l'étudiant.
        """
        return {
            "code omnivox": self.omnivox_code,
            "prénom": self.first_name,
            "nom de famille": self.last_name,
            "alias": self.alias,
            "équipe": self.team,
            "référence d'équipe": self.is_team_reference,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Student":
        """
        Crée une instance de Student à partir d'un dictionnaire.
        """
        return cls(
            omnivox_code=data["code omnivox"],
            first_name=data["prénom"],
            last_name=data["nom de famille"],
            alias=data["alias"],
            team=data.get("équipe"),
            is_team_reference=data.get("référence d'équipe", False),
        )

    def copy(self) -> "Student": # type: ignore
        """
        Retourne une copie de l'étudiant.
        """
        return Student(
            first_name=self.first_name,
            last_name=self.last_name,
            omnivox_code=self.omnivox_code,
            alias=self.alias,
            team=self.team,
            is_team_reference=self.is_team_reference,
        )
