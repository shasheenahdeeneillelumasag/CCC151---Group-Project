from dataclasses import dataclass


@dataclass
class PatientContact:
    contact_id: int | None
    contact_number: str
    patient_id: int
