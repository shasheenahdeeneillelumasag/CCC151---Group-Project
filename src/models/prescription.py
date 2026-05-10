from dataclasses import dataclass
from datetime import date


@dataclass
class Prescription:
    prescription_id: str
    medication_name: str
    dosage: str
    prescribed_date: date
    prescribed_by: str
    record_id: str
