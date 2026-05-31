from PyQt6.QtWidgets import (
    QWidget,
    QFrame,
    QLabel,
    QHBoxLayout,
    QVBoxLayout
)

from PyQt6 import uic

from services.medical_history_service import (
    MedicalHistoryService
)

from dialogs.dialog_add_record import DialogAddRecord

class PageRecords(QWidget):

    def __init__(self, patient_id):
        super().__init__()

        uic.loadUi(
            "ui/page_records.ui",
            self
        )

        self.patient_id = patient_id

        self.history_service = (MedicalHistoryService())

        self.load_records()

        self.searchInput.textChanged.connect(
            self.search_records
        )

        self.btnNewRecord.clicked.connect(
            self.open_add_record_dialog
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

    def populate_records(
        self,
        history
    ):

        self.clear_records()

        for item in history:

            card = self.create_history_card(
                item
            )

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
        frame = QFrame()

        frame.setStyleSheet("""
            QFrame {
                border-bottom: 1px solid #DDE8E3;
                background: white;
            }

            QFrame:hover {
                background: #F8FBFA;
            }
        """)

        root = QHBoxLayout(frame)
        root.setContentsMargins(20, 14, 20, 14)
        root.setSpacing(14)

        # =========================
        # ICON
        # =========================
        icon = QLabel("📋")
        icon.setFixedSize(42, 42)

        icon.setStyleSheet("""
            QLabel {
                background: #EAF3FC;
                border-radius: 10px;
                font-size: 18px;
                padding: 4px;
            }
        """)

        root.addWidget(icon)

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

        root.addLayout(info_layout)
        root.addStretch()

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

        root.addWidget(badge)

        return frame

    def open_add_record_dialog(self):

        dialog = DialogAddRecord(
            self.patient_id
        )

        result = dialog.exec()

        if result:
            self.load_records()

