from PyQt6.QtWidgets import QFrame
from PyQt6 import uic
from PyQt6.QtCore import pyqtSignal

class HistoryCard(QFrame):
    clicked = pyqtSignal()

    def __init__(self, item):
        super().__init__()

        uic.loadUi("ui/card_record.ui", self)

        self.selected = False
        self.item = item

        self.populate(item)

    def populate(self, item):
        record = item.record

        diagnoses = (
            ", ".join(d.diagnosis_name for d in item.diagnoses)
            if item.diagnoses
            else "None recorded"
        )

        prescriptions = (
            ", ".join(
                f"{p.medication_name} ({p.dosage})"
                for p in item.prescriptions
            )
            if item.prescriptions
            else "None prescribed"
        )

        self.lblPurpose.setText(
            f"{record.visit_date} · {record.record_code}"
        )

        self.lblVitals.setText(
            f"BP: {record.blood_pressure or '-'} · "
            f"Weight: {record.weight_kg or '-'} kg"
        )

        self.lblDiagnoses.setText(
            f"Diagnoses: {diagnoses}"
        )

        self.lblPrescriptions.setText(
            f"Rx: {prescriptions}"
        )

        self.lblBadge.setText("VISIT")

    def set_selected(self, selected):
        self.selected = selected

        if selected:
            self.setStyleSheet("""
                QFrame#HistoryCard {
                    background: #EAF7F3;
                    border-bottom: 1px solid #DDE8E3;
                }
            """)

            self.selectionIndicator.setStyleSheet(
                "background: #1A9E78;"
            )

        else:
            self.setStyleSheet("""
                QFrame#HistoryCard {
                    background: white;
                    border-bottom: 1px solid #DDE8E3;
                }
            """)

            self.selectionIndicator.setStyleSheet(
                "background: transparent;"
            )




    def enterEvent(self, event):
        super().enterEvent(event)

    def leaveEvent(self, event):
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)
