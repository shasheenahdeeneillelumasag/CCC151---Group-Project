from PyQt6.QtWidgets import QDialog, QMessageBox
from PyQt6.QtCore import QDate
from PyQt6 import uic

from services.container import appointment_service
from widgets.date_picker import init_date_picker, set_date_picker, get_date_str_from_picker

from datetime import datetime


class DialogAddAppointment(QDialog):

    def __init__(self, patient_id: int, appointment=None):
        super().__init__()
        uic.loadUi("ui/dialog_add_appointment.ui", self)
        self.setFixedSize(700, 480)

        self.appointment_service = appointment_service
        self.patient_id = patient_id
        self._appointment = appointment

        init_date_picker(self.inputDateMonth, self.inputDateDay, self.inputDateYear)
        set_date_picker(self.inputDateMonth, self.inputDateDay, self.inputDateYear, QDate.currentDate())

        self.inputTimeHour.setText("09")
        self.inputTimeMinute.setText("00")
        self.inputTimeAmpm.addItems(["AM", "PM"])

        if self._appointment:
            self.setWindowTitle("Edit Appointment")
            self.btnSave.setText("Update")
            self._prefill()

        self.btnCancel.clicked.connect(self._confirm_cancel)
        self.btnSave.clicked.connect(self._save)

    def _prefill(self):
        a = self._appointment
        self.inputDoctor.setText(a.clinic_name)
        self.inputType.setCurrentText(a.purpose)
        self.inputStatus.setCurrentText(a.status)

        dt = datetime.strptime(str(a.appt_date), "%Y-%m-%d")
        qd = QDate(dt.year, dt.month, dt.day)
        set_date_picker(self.inputDateMonth, self.inputDateDay, self.inputDateYear, qd)

        try:
            parts = a.appt_time.split(":")
            hour = int(parts[0])
            minute = parts[1]
            ampm = "AM" if hour < 12 else "PM"
            if hour == 0:
                hour = 12
            elif hour > 12:
                hour -= 12
            self.inputTimeHour.setText(f"{hour:02d}")
            self.inputTimeMinute.setText(minute)
            self.inputTimeAmpm.setCurrentText(ampm)
        except (ValueError, IndexError):
            pass

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
            QMessageBox.warning(self, "Missing Field", "Doctor or clinic name is required.")
            self.inputDoctor.setFocus()
            return

        status = self.inputStatus.currentText()

        if self._appointment:
            self.appointment_service.update_appointment(
                appointment_id=self._appointment.appointment_id,
                appt_date=appt_date,
                appt_time=appt_time,
                purpose=purpose,
                clinic_name=clinic_name,
                status=status,
                patient_id=self.patient_id,
            )
            QMessageBox.information(self, "Success", "Appointment updated successfully.")
        else:
            self.appointment_service.create_appointment(
                appt_date=appt_date,
                appt_time=appt_time,
                purpose=purpose,
                clinic_name=clinic_name,
                status=status,
                patient_id=self.patient_id,
            )
            QMessageBox.information(self, "Success", "Appointment saved successfully.")

        self.accept()

    def _confirm_cancel(self):
        reply = QMessageBox.question(
            self, "Discard Changes",
            "Are you sure you want to discard the changes?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.reject()
