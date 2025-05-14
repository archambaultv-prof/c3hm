from pydantic import BaseModel, ConfigDict, Field


class Student(BaseModel):
    """
    Représente un étudiant avec un nom, prénom et code Omnivox.
    """
    model_config = ConfigDict(coerce_numbers_to_str=True)

    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)
    omnivox_code: str = Field(..., min_length=1)
    alias: str = Field(..., min_length=1)

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
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Student":
        """
        Crée une instance de Student à partir d'un dictionnaire.
        """
        def one_of(*args):
            for s in args:
                if s in data:
                    return data[s]
            raise KeyError(
                f"Un des champs suivants est requis: {', '.join(args)}"
            )
        return cls(
            first_name=one_of("prénom", "Prénom de l'étudiant"),
            last_name=one_of("nom de famille", "Nom de l'étudiant"),
            omnivox_code=one_of("code omnivox", "No de dossier"),
            alias=data["alias"],
        )

    def copy(self) -> "Student":
        """
        Retourne une copie de l'étudiant.
        """
        return Student(
            first_name=self.first_name,
            last_name=self.last_name,
            omnivox_code=self.omnivox_code,
            alias=self.alias,
        )
