from dataclasses import dataclass
from datetime import date

@dataclass
class Reminder:
    source_type: str
    source_id: int

    title: str
    subtitle: str

    schedule_date: date
    remind_on: date

    status: str
