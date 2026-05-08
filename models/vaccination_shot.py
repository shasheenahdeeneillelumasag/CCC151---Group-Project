from dataclasses import dataclass
from datetime import date


@dataclass
class VaccinationShot:
    vaccine_id: str
    vaccination_name: str
    date_administered: date
    facility: str
    dose_number: int
    schedule_date: date
    status: str
    patient_id: str
