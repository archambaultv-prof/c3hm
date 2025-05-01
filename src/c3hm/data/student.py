from pydantic import BaseModel, Field


class Student(BaseModel):
    """
    Représente un étudiant avec un nom, prénom et code Omnivox.
    """
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
        return cls(
            first_name=data["prénom"],
            last_name=data["nom de famille"],
            omnivox_code=data["code omnivox"],
            alias=data["alias"],
        )
