from PyQt6.QtWidgets import QDialog
from PyQt6.QtCore import QDate, QTime
from PyQt6 import uic

from services.appointment_service import AppointmentService


class DialogAddAppointment(QDialog):

    def __init__(self, patient_id: int):
        super().__init__()
        uic.loadUi("ui/dialog_add_appointment.ui", self)

        self.appointment_service = AppointmentService()
        self.patient_id = patient_id

        self.inputDate.setDate(QDate.currentDate())
        self.inputTime.setTime(QTime(9, 0))

        self.btnCancel.clicked.connect(self.reject)
        self.btnSave.clicked.connect(self._save)

    def _save(self):
        clinic_name = self.inputDoctor.text().strip()
        purpose     = self.inputType.currentText()
        appt_date   = self.inputDate.date().toString("yyyy-MM-dd")
        appt_time   = self.inputTime.time().toString("HH:mm")

        if not clinic_name:
            self.inputDoctor.setFocus()
            return

        self.appointment_service.create_appointment(
            appt_date=appt_date,
            appt_time=appt_time,
            purpose=purpose,
            clinic_name=clinic_name,
            status="Scheduled",
            patient_id=self.patient_id
        )

        self.accept()