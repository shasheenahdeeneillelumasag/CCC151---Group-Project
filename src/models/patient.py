from dataclasses import dataclass
from datetime import date


@dataclass
class Patient:
    patient_id: str
    first_name: str
    last_name: str
    birthdate: date
    sex: str
