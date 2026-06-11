import os
import shutil
from datetime import date

from PyQt6.QtWidgets import QDialog, QFileDialog, QMessageBox
from PyQt6.QtCore import QDate
from PyQt6 import uic

from services.vaccination_shot_service import VaccinationShotService
from services.document_service import DocumentService
from widgets.date_picker import init_date_picker, set_date_picker, get_date_str_from_picker

DOCS_DIR = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "documents")
)


class DialogAddVaccination(QDialog):

    def __init__(self, patient_id: int):
        super().__init__()
        uic.loadUi("ui/dialog_add_vaccination.ui", self)
        self.setFixedSize(self.size())

        self.vaccination_service = VaccinationShotService()
        self.document_service = DocumentService()

        self.patient_id = patient_id
        self._attached_file = None

        self.inputVaccineStatus.currentIndexChanged.connect(self._update_fields)

        init_date_picker(self.inputDateMonth, self.inputDateDay, self.inputDateYear)
        set_date_picker(self.inputDateMonth, self.inputDateDay, self.inputDateYear, QDate.currentDate())



        self.btnCancel.clicked.connect(self._confirm_cancel)
        self.btnSave.clicked.connect(self._save)

        self.uploadZone.mousePressEvent = lambda e: self._pick_file()

        self._update_fields()

    def _dose_number(self) -> int:
        text = self.inputDoseNum.currentText()

        mapping = {
            "Dose 1": 1,
            "Dose 2": 2,
            "Dose 3": 3,
            "Single Dose": 1,
            "Booster": 0
        }

        return mapping.get(text, 1)

    def _pick_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Attach Vaccination Card",
            "",
            "Images (*.jpg *.jpeg *.png);;PDF (*.pdf);;All Files (*)"
        )

        if not path:
            return

        self._attached_file = path

    def _save(self):
        vaccination_name = self.inputVaccineName.text().strip()
        facility = self.inputFacility.text().strip()
        status = self.inputVaccineStatus.currentText()

        selected_date = get_date_str_from_picker(self.inputDateMonth, self.inputDateDay, self.inputDateYear)

        date_administered = None
        schedule_date = None

        if status == "Completed":
            date_administered = selected_date
        else:  # Scheduled or Missed
            schedule_date = selected_date


        if not vaccination_name:
            QMessageBox.warning(self, "Missing Field", "Vaccination name is required.")
            self.inputVaccineName.setFocus()
            return

        if not facility:
            QMessageBox.warning(self, "Missing Field", "Facility name is required.")
            self.inputFacility.setFocus()
            return

        vaccination = self.vaccination_service.create_vaccination(
            vaccination_name=vaccination_name,
            date_administered=date_administered,
            facility=facility,
            dose_number=self._dose_number(),
            schedule_date=schedule_date,
            status=status,
            patient_id=self.patient_id
        )

        if self._attached_file and os.path.exists(self._attached_file):
            os.makedirs(DOCS_DIR, exist_ok=True)

            filename = os.path.basename(self._attached_file)
            dest = os.path.join(DOCS_DIR, filename)

            base, ext = os.path.splitext(filename)
            counter = 1

            while os.path.exists(dest):
                filename = f"{base}_{counter}{ext}"
                dest = os.path.join(DOCS_DIR, filename)
                counter += 1

            shutil.copy2(self._attached_file, dest)

            self.document_service.create_vaccine_document(
                doc_filename=filename,
                date_uploaded=date.today(),
                vaccine_id=vaccination.vaccine_id
            )

        QMessageBox.information(self, "Success", "Vaccination saved successfully.")
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

    def _update_fields(self, status=None):
        status = self.inputVaccineStatus.currentText()

        labels = {
            "Completed": "DATE ADMINISTERED",
            "Pending": "DATE SCHEDULED",
            "Missed": "DATE SCHEDULED"
        }

        self.dateLabel.setText(labels.get(status, "DATE"))
