from PyQt6.QtWidgets import QDialog
from PyQt6 import uic

from services.visit_record_service import VisitRecordService
from services.diagnosis_service import DiagnosisService
from services.prescription_service import PrescriptionService


class DialogAddRecord(QDialog):

    def __init__(self, patient_id):
        super().__init__()
        self.visit_record_service = VisitRecordService()
        self.diagnosis_service = DiagnosisService()
        self.prescription_service = PrescriptionService()

        uic.loadUi(
            "ui/dialog_add_record.ui",
            self
        )

        self.patient_id = patient_id

        self.btnClose.clicked.connect(self.close)
        self.btnCancel.clicked.connect(self.reject)

        self.btnSave.clicked.connect(
            self.save_record
        )

    def save_record(self):

        # Create visit first
        record = self.visit_record_service.create_visit_record(
            visit_date=self.inputVisitDate.date().toPyDate(),
            weight_kg=float(self.inputWeight.text())
                if self.inputWeight.text()
                else None,
            blood_pressure=self.inputBP.text() or None,
            patient_id=self.patient_id
        )

        # Optional diagnosis
        diagnosis_name = self.inputDiagnosis.text().strip()

        if diagnosis_name:

            self.diagnosis_service.create_diagnosis(
                diagnosis_name=diagnosis_name,
                description=self.inputNotes.toPlainText(),
                diagnosed_date=record.visit_date,
                record_id=record.record_id
            )

        # Optional prescription
        rx_text = self.inputRx.toPlainText().strip()

        if rx_text:

            self.prescription_service.create_prescription(
                medication_name=rx_text,
                dosage="",
                prescribed_date=record.visit_date,
                prescribed_by=self.inputDoctor.text(),
                record_id=record.record_id
            )

        self.accept()
