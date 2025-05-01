from pydantic import BaseModel, Field


class Evaluation(BaseModel):
    """
    Information sur une évaluation.
    """
    name: str = Field(..., min_length=1)
    course: str | None = Field(
         default=None,
         min_length=1
         )

    def to_dict(self) -> dict:
        """
        Retourne un dictionnaire représentant l'évaluation.
        """
        return {
            "nom": self.name,
            "cours": self.course,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Evaluation":
        """
        Crée une instance de Evaluation à partir d'un dictionnaire.
        """
        return cls(
            name=data["nom"],
            course=data["cours"],
        )
