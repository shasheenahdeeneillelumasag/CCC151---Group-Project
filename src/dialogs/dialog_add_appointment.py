from PyQt6.QtWidgets import QDialog
from PyQt6.QtCore import QDate
from PyQt6 import uic

from services.appointment_service import AppointmentService
from widgets.date_picker import init_date_picker, set_date_picker, get_date_str_from_picker


class DialogAddAppointment(QDialog):

    def __init__(self, patient_id: int):
        super().__init__()
        uic.loadUi("ui/dialog_add_appointment.ui", self)
        self.setFixedSize(700, 480)

        self.appointment_service = AppointmentService()
        self.patient_id = patient_id

        init_date_picker(self.inputDateMonth, self.inputDateDay, self.inputDateYear)
        set_date_picker(self.inputDateMonth, self.inputDateDay, self.inputDateYear, QDate.currentDate())

        self.inputTimeHour.setText("09")
        self.inputTimeMinute.setText("00")
        self.inputTimeAmpm.addItems(["AM", "PM"])

        self.btnCancel.clicked.connect(self.reject)
        self.btnSave.clicked.connect(self._save)

    def _save(self):
        clinic_name = self.inputDoctor.text().strip()
        purpose     = self.inputType.currentText()
        appt_date   = get_date_str_from_picker(self.inputDateMonth, self.inputDateDay, self.inputDateYear)

        hour = int(self.inputTimeHour.text())
        minute = self.inputTimeMinute.text()
        ampm = self.inputTimeAmpm.currentText()
        if ampm == "PM" and hour != 12:
            hour += 12
        elif ampm == "AM" and hour == 12:
            hour = 0
        appt_time = f"{hour:02d}:{minute}"

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