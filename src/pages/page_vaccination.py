from PyQt6.QtWidgets import (
    QWidget,
    QLabel
)
from PyQt6.QtCore import Qt
from PyQt6 import uic

from services.vaccination_shot_service import VaccinationShotService
from services.patient_service import PatientService
from core.app_settings import AppSettings

from dialogs.dialog_add_vaccination import DialogAddVaccination
from widgets.vaccination_card import VaccinationCard

from models.vaccination_shot import VaccinationShot


class PageVaccinations(QWidget):

    def __init__(self):
        super().__init__()

        uic.loadUi(
            "ui/page_vaccinations.ui",
            self
        )

        self.vaccination_service = VaccinationShotService()
        self.patient_service = PatientService()
        self.settings = AppSettings()

        self.selected_card = None
        self.selected_shot = None

        self.active_patient = (
            self.patient_service.get_patient_by_code(
                self.settings.get_active_patient_code()
            )
            if self.settings.get_active_patient_code()
            else None
        )

        self.patient_id = (
            self.active_patient.patient_id
            if self.active_patient
            else None
        )

        self.btnLogVax.clicked.connect(
            self._open_add_dialog
        )

        self.load_vaccinations()

    def load_vaccinations(self):
        if not self.patient_id:
            return

        shots = (
            self.vaccination_service
            .get_vaccinations_by_patient_id(
                self.patient_id
            )
        )

        self._populate(shots)

    def _populate(
        self,
        shots: list[VaccinationShot]
    ):
        if hasattr(self, "_cards_container"):
            self._cards_container.deleteLater()

        from PyQt6.QtWidgets import (
            QWidget as ContainerWidget,
            QVBoxLayout
        )

        container = ContainerWidget()

        layout = QVBoxLayout(container)
        layout.setContentsMargins(
            0,
            0,
            0,
            0
        )
        layout.setSpacing(12)

        if not shots:

            empty = QLabel(
                "No vaccinations logged yet."
            )

            empty.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            empty.setStyleSheet("""
                font-size: 13px;
                color: #8FA89F;
                padding: 40px 0;
            """)

            layout.addWidget(empty)

        else:

            shots.sort(
                key=lambda s: s.display_date or date.min,
                reverse=True
            )

        for shot in shots:

            card = VaccinationCard(shot)

            card.clicked.connect(
                lambda c=card, s=shot: self.select_vaccination(c, s)
            )

            layout.addWidget(card)

        layout.addStretch()

        scroll_layout = self.scrollContent.layout()

        scroll_layout.insertWidget(
            0,
            container
        )

        self._cards_container = container

    def _open_add_dialog(self):
        dialog = DialogAddVaccination(
            self.patient_id
        )

        if dialog.exec():
            self.load_vaccinations()

    def select_vaccination(self, card, shot):

        if self.selected_card:
            self.selected_card.set_selected(False)

        self.selected_card = card
        self.selected_shot = shot

        card.set_selected(True)
