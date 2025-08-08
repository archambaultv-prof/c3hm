from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from c3hm.data.config.format import Format
from c3hm.data.user_config.evaluation import UserEvaluation


class UserConfig(BaseModel):
    """
    Représente la configuration utilisateur
    """
    model_config = ConfigDict(extra="forbid")

    evaluation: UserEvaluation
    format: Format | None
    students: Path | None = Field(..., description="Chemin vers le fichier des étudiants.")
