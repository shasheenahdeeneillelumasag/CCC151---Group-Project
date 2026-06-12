from datetime import date, datetime, timedelta

from PyQt6.QtWidgets import (
    QWidget, QFrame, QLabel, QHBoxLayout,
    QVBoxLayout, QMessageBox, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6 import uic

from services.container import patient_service, appointment_service
from core.app_settings import AppSettings
from models.appointment import Appointment
from dialogs.dialog_add_appointment import DialogAddAppointment


def _parse_date(value) -> date | None:
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            return None
    return None


def _status_badge_style(status: str) -> tuple[str, str, str]:
    return {
        "Scheduled":  ("#FBDF9E", "#7A4D0A", "Scheduled"),
        "Completed":  ("#D4EDDA", "#155724", "Completed"),
        "Cancelled":  ("#F8D7DA", "#721C24", "Cancelled"),
    }.get(status, ("#F0F0F0", "#555555", status))


class ApptCard(QFrame):
    clicked = pyqtSignal(object)
    reminder_clicked = pyqtSignal(object)

    def __init__(self, appt: Appointment, past: bool = False):
        super().__init__()
        self.appt = appt
        self._selected = False
        self._past = past

        appt_date = _parse_date(appt.appt_date)
        date_str = appt_date.strftime("%B %d, %Y") if appt_date else "—"

        badge_bg, badge_fg, badge_label = _status_badge_style(appt.status)

        remind_on = (appt_date - timedelta(days=2)) if appt_date else None
        today = date.today()
        reminder_active = remind_on and today >= remind_on and appt_date and today < appt_date

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setObjectName("apptCard")
        self.setMinimumHeight(90)

        base = (
            "QFrame#apptCard { background: #FFFFFF; border: 1px solid #DDE8E3; border-radius: 16px; }"
            "QFrame#apptCard:hover { border-color: #9FE1CB; }"
        )
        past_bg = (
            "QFrame#apptCard { background: #FAFCFB; border: 1px solid #DDE8E3; border-radius: 16px; }"
            "QFrame#apptCard:hover { border-color: #9FE1CB; }"
        )
        self.setStyleSheet(past_bg if past else base)

        margin = (18, 22, 18, 22)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(*margin)
        layout.setSpacing(18)

        date_color = "#8FA89F" if past else "#1C2B25"
        lbl_date = QLabel(date_str)
        lbl_date.setStyleSheet(f"font-size: 13px; font-weight: 600; color: {date_color}; border: none; background: transparent;")
        layout.addWidget(lbl_date)

        info_col = QVBoxLayout()
        info_col.setSpacing(4)
        clinic_color = "#546860" if past else "#1C2B25"
        text_color   = "#8FA89F" if past else "#546860"
        lbl_clinic = QLabel(appt.clinic_name)
        lbl_clinic.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {clinic_color}; border: none; background: transparent;")
        lbl_details = QLabel(f"{appt.purpose}  ·  {appt.appt_time}")
        lbl_details.setStyleSheet(f"font-size: 13px; color: {text_color}; border: none; background: transparent;")
        info_col.addWidget(lbl_clinic)
        info_col.addWidget(lbl_details)
        layout.addLayout(info_col, stretch=1)

        right_col = QVBoxLayout()
        right_col.setSpacing(8)
        right_col.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        if appt.status == "Scheduled" and not past:
            bell_color = "#C47B12" if reminder_active else "#C8D9D2"
            bell_bg = "#FEF3DC" if reminder_active else "transparent"
            bell_text = "[!]" if reminder_active else "[]"
            rem_lbl = QLabel(bell_text)
            rem_lbl.setCursor(Qt.CursorShape.PointingHandCursor)
            rem_lbl.setStyleSheet(f"font-size: 15px; color: {bell_color}; background: {bell_bg}; padding: 2px 8px; border-radius: 6px; border: none;")
            rem_lbl.setToolTip("Reminder: " + (remind_on.strftime("%b %d, %Y") if remind_on else "—"))
            rem_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
            rem_lbl.mousePressEvent = lambda e, a=appt: self.reminder_clicked.emit(a)
            right_col.addWidget(rem_lbl)

        badge = QLabel(f"  {badge_label}  ")
        badge.setStyleSheet(f"""
            QLabel {{
                background: transparent;
                color: {badge_fg};
                font-size: 11px;
                font-weight: 700;
                border-radius: 30px;
                padding: 4px 14px;
                border: 2px solid {badge_fg};
            }}
        """)
        badge.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        right_col.addWidget(badge)

        layout.addLayout(right_col)

    def set_selected(self, selected: bool):
        self._selected = selected
        if selected:
            self.setStyleSheet("""
                QFrame#apptCard {
                    background: #E3F5EE;
                    border: 2px solid #1A9E78;
                    border-radius: 16px;
                }
            """)
        else:
            bg = "#FAFCFB" if self._past else "#FFFFFF"
            self.setStyleSheet(f"""
                QFrame#apptCard {{
                    background: {bg};
                    border: 1px solid #DDE8E3;
                    border-radius: 16px;
                }}
                QFrame#apptCard:hover {{
                    border-color: #9FE1CB;
                }}
            """)

    def mousePressEvent(self, event):
        self.clicked.emit(self)
        super().mousePressEvent(event)


class PageAppointments(QWidget):

    def __init__(self):
        super().__init__()
        uic.loadUi("ui/page_appointments.ui", self)

        self.appointment_service = appointment_service
        self.patient_service     = patient_service
        self.settings            = AppSettings()

        self.selected_card = None
        self.selected_appt = None

        self.active_patient = self.patient_service.get_patient_by_code(
            self.settings.get_active_patient_code()
        ) if self.settings.get_active_patient_code() else None
        self.patient_id = self.active_patient.patient_id if self.active_patient else None

        self.btnAddAppt.clicked.connect(self._open_add_dialog)
        self.btnEditAppt.clicked.connect(self._edit_selected)
        self.btnDeleteAppt.clicked.connect(self._delete_selected)
        self.load_appointments()

    def load_appointments(self):
        self.selected_card = None
        self.selected_appt = None
        if not self.patient_id:
            return
        appointments = self.appointment_service.get_appointments_by_patient_id(
            self.patient_id
        )

        today = date.today()

        upcoming = sorted(
            [a for a in appointments
             if a.status == "Scheduled" and _parse_date(a.appt_date) and _parse_date(a.appt_date) >= today],
            key=lambda a: _parse_date(a.appt_date)
        )

        past = sorted(
            [a for a in appointments
             if a.status != "Scheduled" or (_parse_date(a.appt_date) and _parse_date(a.appt_date) < today)],
            key=lambda a: _parse_date(a.appt_date),
            reverse=True
        )

        self._populate_section("UPCOMING", upcoming, 1, past=False)
        self._populate_section("PAST APPOINTMENTS", past, 3, past=True)

    def _populate_section(self, title: str, appointments: list[Appointment], insert_pos: int, past: bool = False):
        if hasattr(self, f"_container_{title}"):
            getattr(self, f"_container_{title}").deleteLater()

        from PyQt6.QtWidgets import QWidget as _W
        container = _W()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(10)

        if not appointments:
            empty = QLabel(f"No {title.lower().replace(' appointments', '')} appointments.")
            empty.setStyleSheet("font-size: 13px; color: #8FA89F; padding: 12px 0;")
            container_layout.addWidget(empty)
        else:
            for appt in appointments:
                card = ApptCard(appt, past=past)
                card.clicked.connect(self._select_card)
                if not past:
                    card.reminder_clicked.connect(self._show_reminder_info)
                container_layout.addWidget(card)

        layout = self.scrollContent.layout()
        layout.insertWidget(insert_pos, container)
        setattr(self, f"_container_{title}", container)

    def _select_card(self, card: ApptCard):
        if self.selected_card:
            self.selected_card.set_selected(False)
        self.selected_card = card
        self.selected_appt = card.appt
        card.set_selected(True)

    def _show_reminder_info(self, appt: Appointment):
        appt_date = _parse_date(appt.appt_date)
        remind_on = (appt_date - timedelta(days=2)) if appt_date else None
        today = date.today()
        status = "Active" if (remind_on and today >= remind_on and appt_date and today < appt_date) else "Pending"
        info = (
            f"Appointment: {appt.purpose}\n"
            f"Clinic: {appt.clinic_name}\n"
            f"Date: {appt.appt_date}\n"
            f"Time: {appt.appt_time}\n"
            f"Remind on: {remind_on.strftime('%B %d, %Y') if remind_on else '—'}\n"
            f"Status: {status}"
        )
        QMessageBox.information(self, "Reminder Details", info)

    def _open_add_dialog(self):
        dialog = DialogAddAppointment(self.patient_id)
        if dialog.exec():
            self.load_appointments()

    def _edit_selected(self):
        if not self.selected_appt:
            QMessageBox.warning(
                self, "No Appointment Selected",
                "Please select an appointment to edit."
            )
            return
        dialog = DialogAddAppointment(self.patient_id, appointment=self.selected_appt)
        if dialog.exec():
            self.load_appointments()

    def _delete_selected(self):
        if not self.selected_appt:
            QMessageBox.warning(
                self, "No Appointment Selected",
                "Please select an appointment to delete."
            )
            return

        a = self.selected_appt
        reply = QMessageBox.question(
            self,
            "Delete Appointment",
            f"Delete the appointment at {a.clinic_name} on {a.appt_date}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        self.appointment_service.delete_appointment(a.appointment_id)
        self.load_appointments()
