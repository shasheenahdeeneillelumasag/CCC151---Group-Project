import os
import shutil
from datetime import date, timedelta

from PyQt6.QtWidgets import QDialog, QFileDialog
from PyQt6.QtCore import QDate
from PyQt6 import uic

from services.vaccination_shot_service import VaccinationShotService
from services.document_service import DocumentService

DOCS_DIR = "documents"

DOSE_INTERVALS = {
    2: 30,
    3: 30,
}


class DialogAddVaccination(QDialog):

    def __init__(self, patient_id: int):
        super().__init__()
        uic.loadUi("ui/dialog_add_vaccination.ui", self)

        self.vaccination_service = VaccinationShotService()
        self.document_service    = DocumentService()
        self.patient_id          = patient_id
        self._attached_file      = None

        self.inputDateAdmin.setDate(QDate.currentDate())

        self.btnClose.clicked.connect(self.reject)
        self.btnCancel.clicked.connect(self.reject)
        self.btnSave.clicked.connect(self._save)
        self.uploadZone.mousePressEvent = lambda e: self._pick_file()

        self.inputTotalDoses.currentIndexChanged.connect(self._update_auto_label)
        self._update_auto_label()

    def _update_auto_label(self):
        total = self._total_doses()
        if total == 1:
            self.autoScheduleLabel.setText(
                "<b>Single-dose vaccine:</b> No follow-up doses required."
            )
        else:
            interval = DOSE_INTERVALS.get(total, 30)
            self.autoScheduleLabel.setText(
                f"<b>Auto-schedule enabled:</b> Next dose will be scheduled "
                f"<b>{interval} days</b> after the date administered."
            )

    def _total_doses(self) -> int:
        text = self.inputTotalDoses.currentText()
        if text.startswith("1"):
            return 1
        elif text.startswith("2"):
            return 2
        return 3

    def _dose_number(self) -> int:
        text = self.inputDoseNum.currentText()
        mapping = {
            "Dose 1": 1, "Dose 2": 2, "Dose 3": 3,
            "Single Dose": 1, "Booster": 1,
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
        filename = os.path.basename(path)
        self.autoScheduleLabel.setText(f"<b>Attached:</b> {filename}")

    def _save(self):
        vaccination_name = self.inputVaccineName.text().strip()
        facility         = self.inputFacility.text().strip()

        if not vaccination_name:
            self.inputVaccineName.setFocus()
            return
        if not facility:
            self.inputFacility.setFocus()
            return

        admin_date  = self.inputDateAdmin.date().toPyDate()
        dose_number = self._dose_number()
        total_doses = self._total_doses()

        schedule_date = None
        if dose_number < total_doses:
            if total_doses == 3 and dose_number == 1:
                schedule_date = admin_date + timedelta(days=30)
            elif total_doses == 3 and dose_number == 2:
                schedule_date = admin_date + timedelta(days=30)
            else:
                schedule_date = admin_date + timedelta(days=DOSE_INTERVALS.get(total_doses, 30))

        status = "Completed" if dose_number >= total_doses else "Pending"

        vaccination = self.vaccination_service.create_vaccination(
            vaccination_name=vaccination_name,
            date_administered=admin_date.strftime("%Y-%m-%d"),
            facility=facility,
            dose_number=dose_number,
            schedule_date=schedule_date.strftime("%Y-%m-%d") if schedule_date else None,
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

        self.accept()