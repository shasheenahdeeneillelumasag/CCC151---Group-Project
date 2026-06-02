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
        self.btnAddDiagnosis.clicked.connect(self.add_diagnosis)
        self.btnAddRx.clicked.connect(self.add_rx)

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
        for i in range(self.listDiagnosis.count()):
            diagnosis_name = self.listDiagnosis.item(i).text().strip()

            self.diagnosis_service.create_diagnosis(
                diagnosis_name=diagnosis_name,
                description=self.inputNotes.toPlainText(),
                diagnosed_date=record.visit_date,
                record_id=record.record_id
            )

        # Optional prescription
        for i in range(self.listRx.count()):
            medication_name = self.listRx.item(i).text().strip()

            self.prescription_service.create_prescription(
                medication_name=medication_name,
                dosage="",
                prescribed_date=record.visit_date,
                prescribed_by=self.inputDoctor.text(),
                record_id=record.record_id
            )

        self.accept()

    def add_diagnosis(self):
        text = self.inputDiagnosisEntry.text().strip()

        if not text:
            return

        self.listDiagnosis.addItem(text)
        self.inputDiagnosisEntry.clear()

    def add_rx(self):
        text = self.inputRxEntry.text().strip()

        if not text:
            return

        self.listRx.addItem(text)
        self.inputRxEntry.clear()
