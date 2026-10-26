"""
Schema for TraduzAI translation CSV.
Must match: id,original,traducao,status,nota
"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Status(str, Enum):
    PENDENTE = "pendente"
    TRADUZIDO = "traduzido"
    IGNORADO = "ignorado"
    ADIADO = "adiado"


@dataclass
class TranslationRow:
    id: str
    original: str
    traducao: str = ""
    status: Status = Status.PENDENTE
    nota: str = ""
    
    def validate(self) -> list[str]:
        errors = []
        if not self.id:
            errors.append("id is required and cannot be changed")
        if self.status not in Status:
            errors.append(f"invalid status: {self.status}")
        return errors


CSV_HEADER = ["id", "original", "traducao", "status", "nota"]
