from PyQt6.QtWidgets import QWidget
from PyQt6 import uic
from PyQt6.QtCore import QDate

from services.patient_service import PatientService


class PageProfile(QWidget):

    def __init__(self, patient_id):
        super().__init__()

        uic.loadUi("ui/page_profile.ui", self)

        self.patient_service = PatientService()

        self.patient_id = patient_id

        self.load_patient()

        self.btnSaveProfile.clicked.connect(
            self.save_profile
        )

        self.btnDiscard.clicked.connect(
            self.load_patient
        )

    def load_patient(self):

        patient = self.patient_service.get_patient_by_id(
            self.patient_id
        )

        if not patient:
            return

        self.inputFirstName.setText(
            patient.first_name
        )

        self.inputLastName.setText(
            patient.last_name
        )

        self.inputSex.setCurrentText(
            patient.sex
        )

        # STRING -> QDate
        birthdate = QDate.fromString(
            patient.birthdate,
            "yyyy-MM-dd"
        )

        self.inputDob.setDate(
            birthdate
        )

        self.heroName.setText(
            f"{patient.first_name} {patient.last_name}"
        )

        self.heroPid.setText(
            f"{patient.patient_code}"
        )

        birthdate = QDate.fromString(patient.birthdate, "yyyy-MM-dd")

        today = QDate.currentDate()
        age = birthdate.daysTo(today) // 365

        self.heroMeta.setText(
            f"{patient.sex}  ·  "
            f"Date of Birth: {birthdate.toString('MMMM d, yyyy')}  ·  "
            f"{age} years old"
        )

    def save_profile(self):

        first_name = self.inputFirstName.text()

        last_name = self.inputLastName.text()

        sex = self.inputSex.currentText()

        # QDate -> STRING
        birthdate = self.inputDob.date().toString(
            "yyyy-MM-dd"
        )

        self.patient_service.update_patient(
            patient_id=self.patient_id,
            first_name=first_name,
            last_name=last_name,
            birthdate=birthdate,
            sex=sex
        )

        self.heroName.setText(
            f"{first_name} {last_name}"
        )
