from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6 import uic


from services.container import vaccination_shot_service, patient_service, document_service
from core.app_settings import AppSettings

from dialogs.dialog_add_vaccination import DialogAddVaccination
from widgets.vaccination_card import VaccinationCard
from widgets.pagination_bar import PaginationBar

from models.vaccination_shot import VaccinationShot


class PageVaccinations(QWidget):

    def __init__(self):
        super().__init__()

        uic.loadUi(
            "ui/page_vaccinations.ui",
            self
        )

        self.vaccination_service = vaccination_shot_service
        self.patient_service = patient_service
        self.document_service = document_service
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

        self._all_shots = []

        self.pagination = PaginationBar()
        self.pagination.page_changed.connect(self._on_page_changed)
        scroll_layout = self.scrollContent.layout()
        scroll_layout.addWidget(self.pagination)

        self.btnLogVax.clicked.connect(self._open_add_dialog)
        self.btnDeleteVax.clicked.connect(self.delete_vaccination)
        self.btnEditVax.clicked.connect(self._edit_selected_vaccination)

        self.load_vaccinations()

    def load_vaccinations(self):
        self.selected_card = None
        self.selected_shot = None


        if not self.patient_id:
            return

        self._all_shots = (
            self.vaccination_service
            .get_vaccinations_by_patient_id(
                self.patient_id
            )
        )

        self._all_shots.sort(
            key=lambda s: s.display_date or date.min,
            reverse=True
        )

        self.pagination.set_total_items(len(self._all_shots))
        self._show_page(0)

    def _on_page_changed(self, page: int):
        self._show_page(page)

    def _show_page(self, page: int):
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

        start = page * self.pagination.page_size()
        shots = self._all_shots[start:start + self.pagination.page_size()]

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

    def _edit_selected_vaccination(self):
        if not self.selected_shot:
            QMessageBox.warning(
                self,
                "No Vaccine Selected",
                "Please select a vaccine first."
            )
            return

        dialog = DialogAddVaccination(
            self.patient_id,
            current_vaccine=self.selected_shot
        )

        if dialog.exec():
            self.load_vaccinations()



    def select_vaccination(self, card, shot):

        if self.selected_card:
            self.selected_card.set_selected(False)

        self.selected_card = card
        self.selected_shot = shot

        card.set_selected(True)

    def delete_vaccination(self):
        if not self.selected_card:
            QMessageBox.warning(
                self, "No Vaccine Selected",
                "Please select a vaccine first."
            )
            return

        reply = QMessageBox.question(
            self, "Delete Vaccine",
            "Are you sure you want to delete this vaccine?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        self.vaccination_service.delete_vaccination(self.selected_shot.vaccine_id)

        self.selected_shot = None
        self.selected_card   = None
        self.load_vaccinations()
