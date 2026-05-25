from dataclasses import dataclass


@dataclass
class PatientContact:
    contact_id: int | None
    patient_code: str
    patient_id: int
