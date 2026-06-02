from dataclasses import dataclass
from datetime import date, time


@dataclass
class Appointment:
    appointment_id: int
    appointment_code: str

    appt_date: date
    appt_time: time
    purpose: str
    clinic_name: str
    status: str
    patient_id: int
