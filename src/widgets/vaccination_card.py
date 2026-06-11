from datetime import date, datetime

from PyQt6.QtWidgets import QFrame
from PyQt6.QtCore import pyqtSignal
from PyQt6 import uic

from models.vaccination_shot import VaccinationShot
from services.document_service import DocumentService

document_service = DocumentService()

def _fmt_date(value) -> str:
    if isinstance(value, date):
        return value.strftime("%B %d, %Y")

    if isinstance(value, str):
        try:
            return datetime.strptime(
                value,
                "%Y-%m-%d"
            ).strftime("%B %d, %Y")
        except ValueError:
            pass

    return "—"

class VaccinationCard(QFrame):
    clicked = pyqtSignal()

    def __init__(self, shot: VaccinationShot):
        super().__init__()

        uic.loadUi("ui/card_vaccination.ui", self)

        self.selected = False
        self.shot = shot

        self.populate()

    def populate(self):
        shot = self.shot

        self.lblVaccineName.setText(
            shot.vaccination_name
        )

        self.lblVaccineMeta.setText(
            f"Vaccine Code: {shot.vaccine_code}, {shot.facility}"
        )

        self.lblDoseDate.setText(
            f"{shot.display_date}"
        )

        self.lblVaxCardPhoto.setText(
            f"{document_service.get_document_by_code(shot.vaccine_code)}"
        )

        self.lblDoseStatus.setText(
            f"{shot.status}"
        )

        if shot.status == "Completed":
            self.lblDoseStatus.setStyleSheet("""
                QLabel {
                    background: #E3F5EE;
                    color: #0D6B52;
                    border-radius: 10px;
                    padding: 4px 10px;
                    font-weight: bold;
                }
            """)

        elif shot.status == "Pending":
            self.lblDoseStatus.setStyleSheet("""
                QLabel {
                    background: #FEF3DC;
                    color: #7A4D0A;
                    border-radius: 10px;
                    padding: 4px 10px;
                    font-weight: bold;
                }
            """)

        else:
            self.lblDoseStatus.setStyleSheet("""
                QLabel {
                    background: #FAE8E8;
                    color: #8A1F1F;
                    border-radius: 10px;
                    padding: 4px 10px;
                    font-weight: bold;
                }
            """)

    def set_selected(self, selected: bool):
        self.selected = selected

        if selected:
            self.setStyleSheet("""
                QFrame#vaxCard {
                    background: #EAF7F3;
                    border: 1px solid #1A9E78;
                    border-radius: 12px;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame#vaxCard {
                    background: white;
                    border: 1px solid #DDE8E3;
                    border-radius: 12px;
                }
            """)

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)
