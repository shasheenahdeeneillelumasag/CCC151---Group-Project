from PyQt6.QtWidgets import QWidget
from PyQt6 import uic
from PyQt6.QtCore import QDate

from services.patient_service import PatientService
from services.patient_contact_service import PatientContactService
from core.app_settings import AppSettings

class PageProfile(QWidget):

    def __init__(self):
        super().__init__()

        uic.loadUi("ui/page_profile.ui", self)

        self.patient_service = PatientService()
        self.contact_service = PatientContactService()
        self.settings = AppSettings()

        self.active_patient = self.patient_service.get_patient_by_code(
            self.settings.get_active_patient_code()
        ) if self.settings.get_active_patient_code() else None
        self.patient_id = self.active_patient.patient_id if self.active_patient else None

        self.contact_id = None

        self.load_patient()

        self.btnSaveProfile.clicked.connect(
            self.save_profile
        )

        self.btnDiscard.clicked.connect(
            self.load_patient
        )

    def load_patient(self):
        if not self.patient_id:
            return

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

        birthdate = QDate.fromString(
            patient.birthdate,
            "yyyy-MM-dd"
        )

        self.inputDob.setDate(
            birthdate
        )

        contacts = self.contact_service.get_contacts_by_patient_id(
            self.patient_id
        )

        if contacts:
            contact = contacts[0]

            self.contact_id = contact.contact_id

            self.inputContact.setText(
                contact.contact_number
            )

        else:
            self.contact_id = None

            self.inputContact.setText("")

        self.heroName.setText(
            f"{patient.first_name} {patient.last_name}"
        )

        initials = (
            (patient.first_name[0] if patient.first_name else "") +
            (patient.last_name[0] if patient.last_name else "")
        ).upper()
        self.avatarInitials.setText(initials)

        self.heroEmail.setText(
            patient.email if hasattr(patient, "email") and patient.email else ""
        )

        if hasattr(self, "inputEmail"):
            self.inputEmail.setText(
                patient.email if hasattr(patient, "email") and patient.email else ""
            )

    def save_profile(self):
        if not self.patient_id:
            return

        first_name = self.inputFirstName.text()

        last_name = self.inputLastName.text()

        sex = self.inputSex.currentText()

        contact_number = self.inputContact.text().strip()

        email = self.inputEmail.text().strip() if hasattr(self, "inputEmail") else ""

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

        if contact_number:

            if self.contact_id is not None:

                self.contact_service.update_contact(
                    contact_id=self.contact_id,
                    patient_id=self.patient_id,
                    contact_number=contact_number
                )

            else:

                contact = self.contact_service.add_contact(
                    patient_id=self.patient_id,
                    contact_number=contact_number
                )

                self.contact_id = contact.contact_id

        self.heroName.setText(
            f"{first_name} {last_name}"
        )

        initials = (
            (first_name[0] if first_name else "") +
            (last_name[0] if last_name else "")
        ).upper()
        self.avatarInitials.setText(initials)

        self.heroEmail.setText(email)