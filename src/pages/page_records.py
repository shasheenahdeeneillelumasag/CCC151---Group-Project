from PyQt6.QtWidgets import (
    QWidget,
    QFrame,
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
    QMessageBox
)

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QFrame
from PyQt6 import uic

from services.medical_history_service import (
    MedicalHistoryService
)

from services.patient_service import PatientService
from services.visit_record_service import VisitRecordService
from core.app_settings import AppSettings
from dialogs.dialog_add_record import DialogAddRecord


class HistoryCard(QFrame):
    clicked = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.selected = False

    def enterEvent(self, event):

        if not self.selected:
            self.content.setStyleSheet("""
                background: #F8FBFA;
            """)

        super().enterEvent(event)

    def leaveEvent(self, event):

        if not self.selected:
            self.content.setStyleSheet("""
                background: white;
            """)

        super().leaveEvent(event)

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)

class PageRecords(QWidget):

    def __init__(self):
        super().__init__()

        uic.loadUi(
            "ui/page_records.ui",
            self
        )

        self.selected_record = None
        self.selected_card = None

        self.patient_service = PatientService()
        self.visit_record_service = VisitRecordService()
        self.settings = AppSettings()

        self.active_patient = self.patient_service.get_patient_by_code(self.settings.get_active_patient_code())
        self.patient_id = self.active_patient.patient_id

        self.history_service = (MedicalHistoryService())

        self.load_records()

        self.searchInput.textChanged.connect(
            self.search_records
        )

        self.btnNewRecord.clicked.connect(
            self.open_add_record_dialog
        )

        self.btnDeleteRecord.clicked.connect(
            self.delete_record
        )

    def load_records(self):

        history = (
            self.history_service
            .get_patient_history(
            self.patient_id
        )
        )

        self.populate_records(history)

    def search_records(self):

        keyword = self.searchInput.text().strip().lower()

        history = self.history_service.get_patient_history(
            self.patient_id
        )

        if not keyword:
            self.populate_records(history)
            return

        filtered = []

        for item in history:

            record = item.record

            diagnoses = " ".join(
                d.diagnosis_name.lower()
                for d in item.diagnoses
            )

            prescriptions = " ".join(
                p.medication_name.lower()
                for p in item.prescriptions
            )

            haystack = (
                f"{record.record_code} "
                f"{record.visit_date} "
                f"{diagnoses} "
                f"{prescriptions}"
            ).lower()

            if keyword in haystack:
                filtered.append(item)

        self.populate_records(filtered)


    def clear_records(self):

        while self.recordsLayout.count():

            item = self.recordsLayout.takeAt(0)

            widget = item.widget()

            if widget:
                widget.deleteLater()

    def populate_records(self, history):
        self.selected_card = None
        self.selected_record = None

        self.clear_records()

        for item in history:
            card = self.create_history_card(item)
            self.recordsLayout.addWidget(card)

        self.recordsLayout.addStretch()

    def create_history_card(self, item):

        record = item.record

        # =========================
        # DIAGNOSES
        # =========================
        if item.diagnoses:
            diagnosis_text = "\n".join(
                f"• {d.diagnosis_name}"
                for d in item.diagnoses
            )
        else:
            diagnosis_text = "• None recorded"

        # =========================
        # PRESCRIPTIONS
        # =========================
        if item.prescriptions:
            prescription_text = "\n".join(
                f"• {p.medication_name} — {p.dosage}"
                for p in item.prescriptions
            )
        else:
            prescription_text = "• None prescribed"

        # =========================
        # ROOT CARD
        # =========================
        frame = HistoryCard()

        frame.setStyleSheet("""
            QFrame {
                border-bottom: 1px solid #DDE8E3;
            }
        """)

        indicator = QWidget()
        indicator.setFixedWidth(4)
        indicator.setStyleSheet("""
            background: transparent;
        """)

        content = QWidget()
        content.setStyleSheet("""
            background: white;
        """)

        frame.indicator = indicator
        frame.content = content

        root = QHBoxLayout(frame)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(indicator)
        root.addWidget(content)

        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(20, 14, 20, 14)
        content_layout.setSpacing(14)

        root.addWidget(indicator)
        root.addWidget(content)

        # =========================
        # ICON
        # =========================
        icon = QLabel("📋")
        icon.setFixedSize(84, 84)

        icon.setStyleSheet("""
            QLabel {
                background: #EAF3FC;
                border-radius: 10px;
                font-size: 36px;
                padding: 4px;
            }
        """)

        content_layout.addWidget(icon)

        # =========================
        # CONTENT AREA
        # =========================
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)

        title = QLabel(
            f"{record.visit_date}  ·  {record.record_code}"
        )

        title.setStyleSheet("""
            font-size: 13px;
            font-weight: bold;
            color: #1C2B25;
        """)

        vitals = QLabel(
            f"BP: {record.blood_pressure or '-'}  ·  "
            f"Weight: {record.weight_kg or '-'} kg"
        )

        vitals.setStyleSheet("""
            font-size: 11px;
            color: #546860;
        """)

        diagnosis_label = QLabel("Diagnoses")
        diagnosis_label.setStyleSheet("""
            font-size: 11px;
            font-weight: bold;
            color: #1C2B25;
            margin-top: 6px;
        """)

        diagnosis_value = QLabel(diagnosis_text)
        diagnosis_value.setWordWrap(True)
        diagnosis_value.setStyleSheet("""
            font-size: 11px;
            color: #546860;
        """)

        prescription_label = QLabel("Prescriptions")
        prescription_label.setStyleSheet("""
            font-size: 11px;
            font-weight: bold;
            color: #1C2B25;
            margin-top: 6px;
        """)

        prescription_value = QLabel(prescription_text)
        prescription_value.setWordWrap(True)
        prescription_value.setStyleSheet("""
            font-size: 11px;
            color: #546860;
        """)

        info_layout.addWidget(title)
        info_layout.addWidget(vitals)
        info_layout.addWidget(diagnosis_label)
        info_layout.addWidget(diagnosis_value)
        info_layout.addWidget(prescription_label)
        info_layout.addWidget(prescription_value)

        content_layout.addLayout(info_layout)
        content_layout.addStretch()

        # =========================
        # BADGE
        # =========================
        badge = QLabel("VISIT")

        badge.setStyleSheet("""
            QLabel {
                background: #E3F5EE;
                color: #0D6B52;
                border-radius: 12px;
                padding: 4px 10px;
                font-size: 10px;
                font-weight: bold;
            }
        """)

        content_layout.addWidget(badge)

        frame.clicked.connect(
            lambda card=frame, data=item:
            self.select_record(card, data)
        )

        return frame

    def open_add_record_dialog(self):

        dialog = DialogAddRecord(
            self.patient_id
        )

        result = dialog.exec()

        if result:
            self.load_records()

    def delete_record(self):

        if not self.selected_record:

            QMessageBox.warning(
                self,
                "No Record Selected",
                "Please select a medical record first."
            )

            return

        reply = QMessageBox.question(
            self,
            "Delete Record",
            "Are you sure you want to delete this record?",
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        record_id = self.selected_record.record.record_id

        self.visit_record_service.delete_visit_record(
            record_id
        )

        self.selected_record = None
        self.selected_card = None

        self.load_records()

    def select_record(self, card, item):

        # reset previous selection
        if self.selected_card:
            self.selected_card.selected = False
            self.selected_card.content.setStyleSheet("""
                background: white;
            """)

            self.selected_card.indicator.setStyleSheet("""
                background: transparent;
            """)

        # apply new selection
        card.selected = True
        card.content.setStyleSheet("""
            background: #EAF7F3;
        """)

        card.indicator.setStyleSheet("""
            background: #1A9E78;
        """)

        self.selected_card = card
        self.selected_record = item
