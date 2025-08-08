from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from c3hm.data.config.evaluation import Evaluation
from c3hm.data.config.format import Format


class Config(BaseModel):
    """
    Représente la configuration utilisateur
    """
    model_config = ConfigDict(extra="forbid")

    evaluation: Evaluation
    format: Format
    students: Path = Field(..., description="Chemin vers le fichier des étudiants.")
