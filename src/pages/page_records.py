from PyQt6.QtWidgets import QWidget, QMessageBox
from PyQt6 import uic

from services.medical_history_service import MedicalHistoryService
from services.patient_service import PatientService
from services.visit_record_service import VisitRecordService
from core.app_settings import AppSettings
from dialogs.dialog_add_record import DialogAddRecord
from dialogs.dialog_edit_record import DialogEditRecord
from widgets.history_card import HistoryCard


class PageRecords(QWidget):

    def __init__(self):
        super().__init__()

        uic.loadUi("ui/page_records.ui", self)

        self.selected_record = None
        self.selected_card   = None

        self.patient_service      = PatientService()
        self.visit_record_service = VisitRecordService()
        self.settings             = AppSettings()

        self.active_patient = self.patient_service.get_patient_by_code(
            self.settings.get_active_patient_code()
        ) if self.settings.get_active_patient_code() else None
        self.patient_id = self.active_patient.patient_id if self.active_patient else None

        self.history_service = MedicalHistoryService()

        self.load_records()

        self.searchInput.textChanged.connect(self.search_records)
        self.btnNewRecord.clicked.connect(self.open_add_record_dialog)
        self.btnEditRecord.clicked.connect(self.open_edit_record_dialog)
        self.btnDeleteRecord.clicked.connect(self.delete_record)

    def load_records(self):
        if not self.patient_id:
            return
        history = self.history_service.get_patient_history(self.patient_id)
        self.populate_records(history)

    def populate_records(self, history):
        self.selected_card   = None
        self.selected_record = None
        self.clear_records()

        for item in history:
            card = self.create_history_card(item)
            self.recordsLayout.addWidget(card)

        self.recordsLayout.addStretch()

    def create_history_card(self, item):
        card = HistoryCard(item)
        card.clicked.connect(
            lambda c=card, i=item: self.select_record(c, i)
        )
        return card

    def search_records(self):
        keyword = self.searchInput.text().strip().lower()
        history = self.history_service.get_patient_history(self.patient_id)

        if not keyword:
            self.populate_records(history)
            return

        filtered = []

        for item in history:
            record = item.record

            diagnosis_text = " ".join(
                f"{d.diagnosis_name} {d.description or ''}"
                for d in item.diagnoses
            )

            rx_text = " ".join(
                f"{p.medication_name} {p.dosage} {p.prescribed_by}"
                for p in item.prescriptions
            )

            haystack = (
                f"{record.record_code} "
                f"{record.visit_date} "
                f"{record.blood_pressure or ''} "
                f"{diagnosis_text} "
                f"{rx_text}"
            ).lower()

            if keyword in haystack:
                filtered.append(item)

        self.populate_records(filtered)

    def clear_records(self):
        while self.recordsLayout.count():
            item   = self.recordsLayout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def open_add_record_dialog(self):
        dialog = DialogAddRecord(self.patient_id)
        if dialog.exec():
            self.load_records()

    def open_edit_record_dialog(self):
        if not self.selected_record:
            QMessageBox.warning(
                self, "No Record Selected",
                "Please select a record to edit."
            )
            return

        dialog = DialogEditRecord(self.selected_record)
        if dialog.exec():
            self.load_records()

    def delete_record(self):
        if not self.selected_record:
            QMessageBox.warning(
                self, "No Record Selected",
                "Please select a medical record first."
            )
            return

        reply = QMessageBox.question(
            self, "Delete Record",
            "Are you sure you want to delete this record?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        self.visit_record_service.delete_visit_record(
            self.selected_record.record.record_id
        )
        self.selected_record = None
        self.selected_card   = None
        self.load_records()

    def select_record(self, card, item):
        if self.selected_card:
            self.selected_card.set_selected(False)
        self.selected_card   = card
        self.selected_record = item
        card.set_selected(True)