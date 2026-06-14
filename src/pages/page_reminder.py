from datetime import date

from PyQt6.QtWidgets import (
    QWidget, QFrame, QLabel, QHBoxLayout,
    QVBoxLayout, QPushButton, QMessageBox,
    QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6 import uic

from services.container import reminder_service, patient_service
from core.app_settings import AppSettings
from models.appointment import Appointment
from models.reminder import Reminder
from models.vaccination_shot import VaccinationShot
from dialogs.dialog_add_appointment import DialogAddAppointment
from dialogs.dialog_add_vaccination import DialogAddVaccination
from widgets.reminder_card import ReminderCard



class PageReminders(QWidget):

    def __init__(self):
        super().__init__()
        uic.loadUi("ui/page_reminders.ui", self)

        self.reminder_service    = reminder_service
        self.patient_service     = patient_service
        self.settings            = AppSettings()

        self.active_patient = self.patient_service.get_patient_by_code(
            self.settings.get_active_patient_code()
        ) if self.settings.get_active_patient_code() else None
        self.patient_id = self.active_patient.patient_id if self.active_patient else None

        self.patient_service.changed.connect(self._on_patient_changed)

        self.reminder_service.changed.connect(self.load_reminders)
        self.load_reminders()

    def _on_patient_changed(self):
        self.active_patient = self.patient_service.get_patient_by_code(
            self.settings.get_active_patient_code()
        ) if self.settings.get_active_patient_code() else None
        self.patient_id = self.active_patient.patient_id if self.active_patient else None
        self.load_reminders()

    def load_reminders(self):
        if not self.patient_id:
            return

        reminders = (
            self.reminder_service
            .get_patient_reminders(self.patient_id)
        )

        flagged = [
            r for r in reminders
            if r.status == "Flagged"
        ]

        upcoming = [
            r for r in reminders
            if r.status == "Upcoming"
        ]

        completed = [
            r for r in reminders
            if r.status == "Completed"
        ]

        dismissed = [
            r for r in reminders
            if r.status == "Dismissed"
        ]

        all_reminders = (
            flagged +
            upcoming +
            completed +
            dismissed
        )

        self._populate_banner(flagged)
        self._populate_list(all_reminders)



    def _populate_banner(self, flagged: list[Reminder]):
        if hasattr(self, "_banner_widget"):
            self._banner_widget.deleteLater()
            del self._banner_widget

        self.activeBanner.hide()

        if not flagged:
            return

        reminder = flagged[0]

        today = date.today()
        days_away = (reminder.schedule_date - today).days

        banner = QFrame()
        banner.setObjectName("activeBannerDyn")
        banner.setStyleSheet("""
            QFrame#activeBannerDyn {
                background: #FEF3DC;
                border: 1.5px solid #FBDF9E;
                border-radius: 14px;
            }
        """)

        layout = QHBoxLayout(banner)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(14)

        bell = QLabel("⚠")
        bell.setFixedSize(42, 42)
        bell.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bell.setStyleSheet("""
            QLabel {
                background: #FBDF9E;
                border-radius: 11px;
                font-size: 18px;
            }
        """)
        layout.addWidget(bell)

        info = QVBoxLayout()
        info.setSpacing(4)

        today_str = today.strftime("%B %d, %Y").upper()

        lbl_eyebrow = QLabel(
            f"REMINDER FLAGGED — TODAY IS {today_str}"
        )
        lbl_eyebrow.setStyleSheet(
            "font-size: 9px; font-weight: bold; color: #C47B12;"
        )
        info.addWidget(lbl_eyebrow)

        if days_away == 0:
            body = f"{reminder.title} is scheduled today"
        elif days_away == 1:
            body = f"Prepare for {reminder.title} tomorrow"
        else:
            body = f"Prepare for {reminder.title} in {days_away} days"

        lbl_body = QLabel(body)
        lbl_body.setStyleSheet(
            "font-size: 14px; font-weight: bold; color: #3D2800;"
        )
        info.addWidget(lbl_body)

        lbl_detail = QLabel(
            f"{reminder.schedule_date:%B %d, %Y}  ·  {reminder.subtitle}"
        )
        lbl_detail.setStyleSheet(
            "font-size: 11px; color: #7A4D0A;"
        )
        info.addWidget(lbl_detail)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        btn_view = QPushButton("View Details")
        btn_view.setStyleSheet("""
            QPushButton {
                background: #C47B12;
                color: white;
                font-size: 11px;
                font-weight: 600;
                border: none;
                border-radius: 6px;
                padding: 6px 14px;
            }
            QPushButton:hover {
                background: #7A4D0A;
            }
        """)
        btn_view.clicked.connect(
            lambda: self._open_reminder(reminder)
        )

        btn_dismiss = QPushButton("Dismiss")
        btn_dismiss.setStyleSheet("""
            QPushButton {
                background: rgba(196,123,18,0.12);
                color: #7A4D0A;
                font-size: 11px;
                font-weight: 600;
                border: none;
                border-radius: 6px;
                padding: 6px 14px;
            }
            QPushButton:hover {
                background: rgba(196,123,18,0.22);
            }
        """)
        btn_dismiss.clicked.connect(
            lambda: self._dismiss(reminder)
        )

        btn_row.addWidget(btn_view)
        btn_row.addWidget(btn_dismiss)
        btn_row.addStretch()

        info.addLayout(btn_row)

        layout.addLayout(info)

        self.scrollContent.layout().insertWidget(0, banner)

        self._banner_widget = banner
       
    def _populate_list(self, reminders: list[Reminder]):
        if hasattr(self, "_list_container"):
            self._list_container.deleteLater()

        self.remList.hide()

        if not reminders:
            empty = QLabel(
                "No reminders available."
            )

            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)

            empty.setStyleSheet("""
                font-size: 13px;
                color: #8FA89F;
                padding: 20px 0;
            """)

            idx = 2 if hasattr(self, "_banner_widget") else 1

            self.scrollContent.layout().insertWidget(idx, empty)

            self._list_container = empty
            return

        list_frame = QFrame()
        list_frame.setObjectName("remListDyn")

        list_frame.setStyleSheet("""
            QFrame#remListDyn {
                background: white;
                border: 1px solid #DDE8E3;
                border-radius: 14px;
            }
        """)

        list_layout = QVBoxLayout(list_frame)
        list_layout.setContentsMargins(0, 0, 0, 0)
        list_layout.setSpacing(0)

        for reminder in reminders:
            card = ReminderCard(reminder)
            card.clicked.connect(self._open_reminder)
            list_layout.addWidget(card)

        idx = 2 if hasattr(self, "_banner_widget") else 1

        self.scrollContent.layout().insertWidget(
            idx,
            list_frame
        )

        self._list_container = list_frame


    def _open_reminder(self, reminder: Reminder):

        if reminder.source_type == "appointment":

            appt = (
                self.reminder_service
                .appointment_service
                .get_appointment_by_id(
                    reminder.source_id
                )
            )

            if not appt:
                return

            dialog = DialogAddAppointment(
                patient_id=appt.patient_id,
                appointment=appt
            )

            dialog.exec()

        elif reminder.source_type == "vaccination":
            vac = (self.reminder_service.vaccination_shot_service.get_vaccination_by_id(reminder.source_id))

            if not vac:
                return

            dialog = DialogAddVaccination(
                patient_id=vac.patient_id,
                current_vaccine=vac
            )
            
            dialog.exec()


    def _dismiss(self, reminder: Reminder):
        if (
            QMessageBox.question(
                self,
                "Dismiss Reminder",
                f"Dismiss '{reminder.title}'?",
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No
            )
            != QMessageBox.StandardButton.Yes
        ):
            return

        self.reminder_service.dismiss(reminder)
        self.load_reminders()

