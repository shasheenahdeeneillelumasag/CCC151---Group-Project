from dataclasses import dataclass
from datetime import date

@dataclass
class Patient:
    patient_id: int
    patient_code: str

    first_name: str
    last_name: str
    birthdate: date
    sex: str
