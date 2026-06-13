from models.reminder import Reminder

from services.appointment_service import AppointmentService
from services.vaccination_shot_service import VaccinationShotService
from PyQt6.QtCore import QObject, pyqtSignal
from datetime import date, timedelta, datetime

def parse_date(value) -> date | None:
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            return None
    return None


def fmt_date(value) -> str:
    d = _parse_date(value)
    return d.strftime("%B %d, %Y") if d else "—"



class ReminderService(QObject):
    changed = pyqtSignal()

    def __init__(self, appointment_service: AppointmentService, vaccination_shot_service: VaccinationShotService):
        super().__init__()
        self.appointment_service = appointment_service
        self.vaccination_shot_service = vaccination_shot_service

    def get_patient_reminders(self, patient_id: int)-> list[Reminder]:

        reminders = []

        reminders.extend(self._get_appointment_reminders(patient_id))
        reminders.extend(self._get_vaccination_reminders(patient_id))

        reminders.sort(key=lambda r: r.schedule_date)

        return reminders

    def get_active_patient_reminders(self,patient_id: int) -> list[Reminder]:

        reminders = self.get_patient_reminders(patient_id)

        return [
            reminder
            for reminder in reminders
            if reminder.status in (
                "Upcoming",
                "Flagged"
            )
        ]


    def _get_appointment_reminders(self,patient_id: int) -> list[Reminder]:

        reminders = []

        appointments = (
            self.appointment_service
            .get_appointments_by_patient_id(patient_id)
        )

        for appt in appointments:
            appt_date = parse_date(appt.appt_date)

            reminders.append(
                Reminder(
                    source_type="appointment",
                    source_id=appt.appointment_id,

                    title=appt.purpose,
                    subtitle=appt.clinic_name,

                    schedule_date=appt_date,
                    remind_on=appt_date - timedelta(days=2),

                    status=self._compute_status(
                        appt_date,
                        appt.status
                    )
                )
            )

        return reminders

    def _get_vaccination_reminders(self,patient_id: int) -> list[Reminder]:
        reminders = []

        vaccinations = (
            self.vaccination_shot_service
            .get_vaccinations_by_patient_id(patient_id)
        )

        for shot in vaccinations:

            if shot.status == "Completed":
                continue

            if not shot.schedule_date:
                continue

            schedule_date = parse_date(shot.schedule_date)

            reminders.append(
                Reminder(
                    source_type="vaccination",
                    source_id=shot.vaccine_id,

                    title=shot.vaccination_name,
                    subtitle=f"Dose {shot.display_dose}",

                    schedule_date=schedule_date,
                    remind_on=schedule_date - timedelta(days=2),

                    status=self._compute_status(
                        schedule_date,
                        shot.status
                    )
                )
            )

        return reminders



    def _compute_status(self, schedule_date: date, source_status: str) -> str:
        today = date.today()

        if source_status == "Cancelled":
            return "Dismissed"

        if source_status == "Completed":
            return "Completed"

        if today > schedule_date:
            return "Completed"

        if today >= schedule_date - timedelta(days=2):
            return "Flagged"

        return "Upcoming"
