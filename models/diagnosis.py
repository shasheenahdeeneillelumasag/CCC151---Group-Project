from dataclasses import dataclass
from datetime import date


@dataclass
class Diagnosis:
    diagnosis_id: str
    diagnosis_name: str
    description: str | None
    diagnosed_date: date
    record_id: str
