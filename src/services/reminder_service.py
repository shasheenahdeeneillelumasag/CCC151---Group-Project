from models.reminder import Reminder

from services.appointment_service import AppointmentService
from services.vaccination_shot_service import VaccinationShotService
from PyQt6.QtCore import QObject, pyqtSignal
from datetime import date, timedelta, datetime, time


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

def parse_time(value) -> time | None:
    if isinstance(value, time):
        return value

    if isinstance(value, str):
        formats = [
            "%H:%M",      # 14:30
            "%H:%M:%S",   # 14:30:00
            "%I:%M %p",   # 2:30 PM
        ]

        for fmt in formats:
            try:
                return datetime.strptime(value, fmt).time()
            except ValueError:
                pass

    return None

def fmt_time(value) -> str:
    t = parse_time(value)
    return t.strftime("%I:%M %p") if t else "—"


class ReminderService(QObject):
    changed = pyqtSignal()

    def __init__(self, appointment_service: AppointmentService, vaccination_shot_service: VaccinationShotService):
        super().__init__()
        self.appointment_service = appointment_service
        self.vaccination_shot_service = vaccination_shot_service


        self.appointment_service.changed.connect(self._on_source_changed)
        self.vaccination_shot_service.changed.connect(self._on_source_changed)

    def dismiss(self, current_reminder: Reminder):
        if current_reminder.source_type == "appointment":
            appt = (self.appointment_service.get_appointment_by_id(current_reminder.source_id))

            if not appt:
                return

            self.appointment_service.update_appointment(
                appointment_id=appt.appointment_id,
                appt_date=appt.appt_date,
                appt_time=appt.appt_time,
                purpose=appt.purpose,
                clinic_name=appt.clinic_name,
                status="Cancelled",
                patient_id=appt.patient_id
            )

        if current_reminder.source_type == "vaccination":
            vac = self.vaccination_shot_service.get_vaccination_by_id(current_reminder.source_id)

            if not vac:
                return

            self.vaccination_shot_service.update_vaccination(
                vaccine_id=vac.vaccine_id,
                vaccination_name=vac.vaccination_name,
                date_administered=vac.date_administered,
                facility=vac.facility,
                dose_number=vac.dose_number,
                schedule_date=vac.schedule_date,
                status="Missed",
                patient_id=vac.patient_id
            )
            

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
                    subtitle_2=fmt_time(appt.appt_time),

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
                    subtitle_2=None,

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

        if source_status == "Missed":
            return "Dismissed"

        if source_status == "Cancelled":
            return "Dismissed"

        if source_status == "Completed":
            return "Completed"

        if today > schedule_date:
            return "Completed"

        if today >= schedule_date - timedelta(days=2):
            return "Flagged"

        return "Upcoming"

    def _on_source_changed(self):
        self.changed.emit()
