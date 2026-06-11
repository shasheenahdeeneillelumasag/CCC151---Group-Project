from dataclasses import dataclass
from datetime import date


@dataclass
class VaccinationShot:
    vaccine_id: int | None
    vaccine_code: str | None

    vaccination_name: str
    date_administered: date

    facility: str
    dose_number: int

    schedule_date: date | None
    status: str

    patient_id: int

    @property
    def display_date(self):
        if self.status == "Completed":
            return self.date_administered

        return self.schedule_date
