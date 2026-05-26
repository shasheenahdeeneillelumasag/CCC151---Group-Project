from PyQt6.QtWidgets import QWidget
from PyQt6 import uic
from PyQt6.QtCore import QDate

from services.patient_service import PatientService
from services.patient_contact_service import PatientContactService


class PageProfile(QWidget):

    def __init__(self, patient_id):
        super().__init__()

        uic.loadUi("ui/page_profile.ui", self)

        self.patient_service = PatientService()
        self.contact_service = PatientContactService()

        self.patient_id = patient_id

        # keep track of current contact row
        self.contact_id = None

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

        # =========================
        # LOAD CONTACT NUMBER
        # =========================

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

        # =========================
        # HERO SECTION
        # =========================

        self.heroName.setText(
            f"{patient.first_name} {patient.last_name}"
        )

        self.heroPid.setText(
            f"{patient.patient_code}"
        )

        today = QDate.currentDate()

        age = birthdate.daysTo(today) // 365

        self.heroMeta.setText(
            f"{patient.sex}  ·  "
            f"Date of Birth: "
            f"{birthdate.toString('MMMM d, yyyy')}  ·  "
            f"{age} years old"
        )

    def save_profile(self):

        first_name = self.inputFirstName.text()

        last_name = self.inputLastName.text()

        sex = self.inputSex.currentText()

        contact_number = self.inputContact.text().strip()

        # QDate -> STRING
        birthdate = self.inputDob.date().toString(
            "yyyy-MM-dd"
        )

        # =========================
        # UPDATE PATIENT
        # =========================

        self.patient_service.update_patient(
            patient_id=self.patient_id,
            first_name=first_name,
            last_name=last_name,
            birthdate=birthdate,
            sex=sex
        )

        # =========================
        # UPDATE / CREATE CONTACT
        # =========================

        if contact_number:

            # update existing
            if self.contact_id is not None:

                self.contact_service.update_contact(
                    contact_id=self.contact_id,
                    patient_id=self.patient_id,
                    contact_number=contact_number
                )

            # create new
            else:

                contact = self.contact_service.add_contact(
                    patient_id=self.patient_id,
                    contact_number=contact_number
                )

                self.contact_id = contact.contact_id

        # =========================
        # UPDATE HERO
        # =========================

        self.heroName.setText(
            f"{first_name} {last_name}"
        )

        birthdate_qdate = QDate.fromString(
            birthdate,
            "yyyy-MM-dd"
        )

        today = QDate.currentDate()

        age = birthdate_qdate.daysTo(today) // 365

        self.heroMeta.setText(
            f"{sex}  ·  "
            f"Date of Birth: "
            f"{birthdate_qdate.toString('MMMM d, yyyy')}  ·  "
            f"{age} years old"
        )
