from dataclasses import dataclass


@dataclass
class PatientContact:
    contact_id: int | None
    patient_id: str
    contact_number: str
