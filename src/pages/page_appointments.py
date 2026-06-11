from datetime import date, datetime, timedelta

from PyQt6.QtWidgets import (
    QWidget, QFrame, QLabel, QHBoxLayout,
    QVBoxLayout, QMessageBox, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6 import uic

from services.appointment_service import AppointmentService
from services.patient_service import PatientService
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


def _status_badge_style(status: str) -> tuple[str, str]:
    return {
        "Scheduled":  ("#FBDF9E", "#7A4D0A"),
        "Completed":  ("#E8F5EB", "#1F5C2E"),
        "Cancelled":  ("#FAE8E8", "#8A1F1F"),
    }.get(status, ("#F0F0F0", "#555555"))


class ApptCard(QFrame):
    delete_requested = pyqtSignal(object)
    reminder_clicked = pyqtSignal(object)

    def __init__(self, appt: Appointment, show_divider: bool = False):
        super().__init__()
        self.appt = appt

        appt_date = _parse_date(appt.appt_date)
        day   = appt_date.strftime("%d")   if appt_date else "—"
        month = appt_date.strftime("%b %Y").upper() if appt_date else "—"

        badge_bg, badge_fg = _status_badge_style(appt.status)

        remind_on = (appt_date - timedelta(days=2)) if appt_date else None
        today = date.today()
        reminder_active = remind_on and today >= remind_on and today < appt_date if appt_date else False

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        if show_divider:
            divider = QFrame()
            divider.setFrameShape(QFrame.Shape.HLine)
            divider.setStyleSheet("QFrame { color: #DDE8E3; margin: 0 20px; }")
            outer.addWidget(divider)

        row = QHBoxLayout()
        row.setContentsMargins(20, 14, 20, 14)
        row.setSpacing(14)

        date_col = QVBoxLayout()
        date_col.setSpacing(0)
        lbl_day = QLabel(day)
        lbl_day.setStyleSheet("font-size: 22px; font-weight: 800; color: #1C2B25;")
        lbl_mon = QLabel(month)
        lbl_mon.setStyleSheet("font-size: 9px; color: #8FA89F;")
        date_col.addWidget(lbl_day)
        date_col.addWidget(lbl_mon)
        row.addLayout(date_col)

        info_col = QVBoxLayout()
        info_col.setSpacing(3)
        lbl_clinic = QLabel(appt.clinic_name)
        lbl_clinic.setStyleSheet("font-size: 13px; font-weight: bold; color: #1C2B25;")
        lbl_details = QLabel(f"{appt.purpose}  ·  {appt.appt_time}")
        lbl_details.setStyleSheet("font-size: 11px; color: #546860;")
        info_col.addWidget(lbl_clinic)
        info_col.addWidget(lbl_details)
        row.addLayout(info_col)

        row.addStretch()

        right_col = QVBoxLayout()
        right_col.setSpacing(6)
        right_col.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        if appt.status == "Scheduled":
            bell_color = "#C47B12" if reminder_active else "#C8D9D2"
            bell_bg = "#FEF3DC" if reminder_active else "transparent"
            rem_lbl = QLabel("[!]" if reminder_active else "[]")
            rem_lbl.setCursor(Qt.CursorShape.PointingHandCursor)
            rem_lbl.setStyleSheet(f"font-size: 13px; color: {bell_color}; background: {bell_bg}; padding: 1px 6px; border-radius: 4px;")
            rem_lbl.setToolTip("Reminder: " + (remind_on.strftime("%b %d, %Y") if remind_on else "—"))
            rem_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
            rem_lbl.mousePressEvent = lambda e, a=appt: self.reminder_clicked.emit(a)
            right_col.addWidget(rem_lbl)

        badge = QLabel(f"  {appt.status}  ")
        badge.setStyleSheet(f"""
            QLabel {{
                background: {badge_bg};
                color: {badge_fg};
                font-size: 10px;
                font-weight: bold;
                border-radius: 20px;
                padding: 2px 10px;
            }}
        """)
        badge.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        right_col.addWidget(badge)

        del_lbl = QLabel("[Del]")
        del_lbl.setCursor(Qt.CursorShape.PointingHandCursor)
        del_lbl.setStyleSheet("font-size: 13px; color: #C0C0C0;")
        del_lbl.setToolTip("Delete appointment")
        del_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        del_lbl.mousePressEvent = lambda e, a=appt: self.delete_requested.emit(a)
        right_col.addWidget(del_lbl)

        row.addLayout(right_col)
        outer.addLayout(row)


class PageAppointments(QWidget):

    def __init__(self):
        super().__init__()
        uic.loadUi("ui/page_appointments.ui", self)

        self.appointment_service = AppointmentService()
        self.patient_service     = PatientService()
        self.settings            = AppSettings()

        self.active_patient = self.patient_service.get_patient_by_code(
            self.settings.get_active_patient_code()
        ) if self.settings.get_active_patient_code() else None
        self.patient_id = self.active_patient.patient_id if self.active_patient else None

        self.btnAddAppt.clicked.connect(self._open_add_dialog)
        self.load_appointments()

    def load_appointments(self):
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

        self._populate_section("UPCOMING", upcoming, 1)
        self._populate_section("PAST APPOINTMENTS", past, 3)

    def _populate_section(self, title: str, appointments: list[Appointment], insert_pos: int):
        if hasattr(self, f"_container_{title}"):
            getattr(self, f"_container_{title}").deleteLater()

        from PyQt6.QtWidgets import QWidget as _W
        container = _W()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(12 if title == "UPCOMING" else 0)

        if not appointments:
            empty = QLabel(f"No {title.lower().replace(' appointments', '')} appointments.")
            empty.setStyleSheet("font-size: 13px; color: #8FA89F; padding: 12px 0;")
            container_layout.addWidget(empty)
        else:
            card = QFrame()
            card.setStyleSheet("""
                QFrame {
                    background: #FFFFFF;
                    border: 1px solid #DDE8E3;
                    border-radius: 14px;
                }
            """)
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(0, 0, 0, 0)
            card_layout.setSpacing(0)

            for i, appt in enumerate(appointments):
                row = ApptCard(appt, show_divider=(i > 0))
                row.delete_requested.connect(self._delete_appointment)
                row.reminder_clicked.connect(self._show_reminder_info)
                card_layout.addWidget(row)

            container_layout.addWidget(card)

        layout = self.scrollContent.layout()
        layout.insertWidget(insert_pos, container)
        setattr(self, f"_container_{title}", container)

    def _show_reminder_info(self, appt: Appointment):
        appt_date = _parse_date(appt.appt_date)
        remind_on = (appt_date - timedelta(days=2)) if appt_date else None
        today = date.today()
        status = "Active" if (remind_on and today >= remind_on and today < appt_date if appt_date else False) else "Pending"
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

    def _delete_appointment(self, appt: Appointment):
        reply = QMessageBox.question(
            self,
            "Delete Appointment",
            f"Delete the appointment at {appt.clinic_name} on {appt.appt_date}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        self.appointment_service.delete_appointment(appt.appointment_id)
        self.load_appointments()
