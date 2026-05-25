from dataclasses import dataclass
from datetime import date


@dataclass
class VisitRecord:
    record_id: int
    record_code: str

    visit_date: date
    weight_kg: float | None
    blood_pressure: str | None
    patient_id: int
