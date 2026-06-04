from datetime import date, datetime

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
    """Return (bg, fg) for a status badge."""
    return {
        "Scheduled":  ("#FBDF9E", "#7A4D0A"),
        "Completed":  ("#E8F5EB", "#1F5C2E"),
        "Cancelled":  ("#FAE8E8", "#8A1F1F"),
    }.get(status, ("#F0F0F0", "#555555"))

class AppointmentRow(QFrame):
    delete_requested = pyqtSignal(object)

    def __init__(self, appt: Appointment, show_divider: bool = False):
        super().__init__()
        self.appt = appt

        appt_date = _parse_date(appt.appt_date)
        day   = appt_date.strftime("%d")   if appt_date else "—"
        month = appt_date.strftime("%b %Y").upper() if appt_date else "—"

        badge_bg, badge_fg = _status_badge_style(appt.status)

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
        lbl_day.setStyleSheet("font-size: 22px; font-weight: 800; color: #8FA89F;")
        lbl_mon = QLabel(month)
        lbl_mon.setStyleSheet("font-size: 9px; color: #8FA89F;")
        date_col.addWidget(lbl_day)
        date_col.addWidget(lbl_mon)
        row.addLayout(date_col)

        info_col = QVBoxLayout()
        info_col.setSpacing(3)
        lbl_clinic = QLabel(appt.clinic_name)
        lbl_clinic.setStyleSheet("font-size: 13px; font-weight: bold; color: #1C2B25;")
        lbl_purpose = QLabel(f"{appt.purpose}  ·  {appt.appt_time}")
        lbl_purpose.setStyleSheet("font-size: 11px; color: #546860;")
        info_col.addWidget(lbl_clinic)
        info_col.addWidget(lbl_purpose)
        row.addLayout(info_col)

        row.addStretch()

        right_col = QVBoxLayout()
        right_col.setSpacing(6)
        right_col.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

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

        del_lbl = QLabel("🗑")
        del_lbl.setCursor(Qt.CursorShape.PointingHandCursor)
        del_lbl.setStyleSheet("font-size: 13px; color: #C0C0C0;")
        del_lbl.setToolTip("Delete appointment")
        del_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        del_lbl.mousePressEvent = lambda e, a=appt: self.delete_requested.emit(a)
        right_col.addWidget(del_lbl)

        row.addLayout(right_col)
        outer.addLayout(row)


# Upcoming appointment card 

class UpcomingCard(QFrame):
    delete_requested = pyqtSignal(object)

    def __init__(self, appt: Appointment):
        super().__init__()
        self.appt = appt
        self.setObjectName("upcomingCard")
        self.setStyleSheet("""
            QFrame#upcomingCard {
                background: #FFFFFF;
                border: 1px solid #DDE8E3;
                border-radius: 14px;
            }
        """)

        appt_date = _parse_date(appt.appt_date)
        today     = date.today()

        day        = appt_date.strftime("%d")            if appt_date else "—"
        month_year = appt_date.strftime("%b %Y").upper() if appt_date else "—"

        days_until = (appt_date - today).days if appt_date else None
        reminder_date = None
        if appt_date:
            from datetime import timedelta
            reminder_date = appt_date - timedelta(days=2)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(18)

        cal = QFrame()
        cal.setObjectName("calBlock")
        cal.setFixedSize(60, 60)
        cal.setStyleSheet("""
            QFrame#calBlock {
                background: #E3F5EE;
                border-radius: 12px;
            }
        """)
        cal_layout = QVBoxLayout(cal)
        cal_layout.setSpacing(0)
        cal_layout.setContentsMargins(4, 6, 4, 6)

        lbl_day = QLabel(day)
        lbl_day.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_day.setStyleSheet("font-size: 26px; font-weight: 800; color: #1A9E78;")

        lbl_mon = QLabel(month_year)
        lbl_mon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_mon.setStyleSheet("font-size: 8px; font-weight: 700; color: #8FA89F; letter-spacing: 0.5px;")

        cal_layout.addWidget(lbl_day)
        cal_layout.addWidget(lbl_mon)
        layout.addWidget(cal)

        info = QVBoxLayout()
        info.setSpacing(5)

        lbl_clinic = QLabel(appt.clinic_name)
        lbl_clinic.setStyleSheet("font-size: 14px; font-weight: bold; color: #1C2B25;")
        info.addWidget(lbl_clinic)

        lbl_purpose = QLabel(f"{appt.purpose}")
        lbl_purpose.setStyleSheet("font-size: 12px; color: #546860;")
        info.addWidget(lbl_purpose)

        if reminder_date:
            reminder_str = reminder_date.strftime("%B %d, %Y")
            lbl_reminder = QLabel(f"🔔  Reminder auto-set: {reminder_str}  (2 days before)")
            lbl_reminder.setStyleSheet("font-size: 11px; color: #C47B12; font-weight: 600;")
            info.addWidget(lbl_reminder)

        layout.addLayout(info)
        layout.addStretch()

        right = QVBoxLayout()
        right.setSpacing(6)
        right.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        lbl_time = QLabel(str(appt.appt_time))
        lbl_time.setAlignment(Qt.AlignmentFlag.AlignRight)
        lbl_time.setStyleSheet("font-size: 12px; color: #8FA89F;")
        right.addWidget(lbl_time)

        if days_until is not None and days_until <= 2:
            badge = QLabel("  Reminder Active  ")
            badge.setStyleSheet("""
                QLabel {
                    background: #FBDF9E;
                    color: #7A4D0A;
                    font-size: 10px;
                    font-weight: bold;
                    border-radius: 20px;
                    padding: 2px 4px;
                }
            """)
            badge.setAlignment(Qt.AlignmentFlag.AlignRight)
            right.addWidget(badge)

        del_lbl = QLabel("🗑")
        del_lbl.setCursor(Qt.CursorShape.PointingHandCursor)
        del_lbl.setStyleSheet("font-size: 13px; color: #C0C0C0;")
        del_lbl.setToolTip("Delete appointment")
        del_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        del_lbl.mousePressEvent = lambda e, a=appt: self.delete_requested.emit(a)
        right.addWidget(del_lbl)

        layout.addLayout(right)


#  Main page 

class PageAppointments(QWidget):

    def __init__(self):
        super().__init__()
        uic.loadUi("ui/page_appointments.ui", self)

        self.appointment_service = AppointmentService()
        self.patient_service     = PatientService()
        self.settings            = AppSettings()

        self.active_patient = self.patient_service.get_patient_by_code(
            self.settings.get_active_patient_code()
        )
        self.patient_id = self.active_patient.patient_id

        self.btnAddAppt.clicked.connect(self._open_add_dialog)

        self.load_appointments()

    #  Load 

    def load_appointments(self):
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

        self._populate_upcoming(upcoming)
        self._populate_past(past)

    # Populate upcoming 

    def _populate_upcoming(self, appointments: list[Appointment]):

        layout = self.scrollContent.layout()

        if hasattr(self, "_upcoming_container"):
            self._upcoming_container.deleteLater()

        from PyQt6.QtWidgets import QWidget as _W
        container = _W()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(12)

        if not appointments:
            empty = QLabel("No upcoming appointments.")
            empty.setStyleSheet("font-size: 13px; color: #8FA89F; padding: 12px 0;")
            container_layout.addWidget(empty)
        else:
            for appt in appointments:
                card = UpcomingCard(appt)
                card.delete_requested.connect(self._delete_appointment)
                container_layout.addWidget(card)

                if appt == appointments[0]:
                    track = self._build_lifecycle_track(appt)
                    container_layout.addWidget(track)

        layout.insertWidget(1, container)
        self._upcoming_container = container

    # Populate past 

    def _populate_past(self, appointments: list[Appointment]):
        if hasattr(self, "_past_container"):
            self._past_container.deleteLater()

        from PyQt6.QtWidgets import QWidget as _W
        container = _W()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        if not appointments:
            empty = QLabel("No past appointments.")
            empty.setStyleSheet("font-size: 13px; color: #8FA89F; padding: 12px 0;")
            container_layout.addWidget(empty)
        else:
            past_card = QFrame()
            past_card.setObjectName("pastCard")
            past_card.setStyleSheet("""
                QFrame#pastCard {
                    background: #FFFFFF;
                    border: 1px solid #DDE8E3;
                    border-radius: 14px;
                }
            """)
            past_card_layout = QVBoxLayout(past_card)
            past_card_layout.setContentsMargins(0, 0, 0, 0)
            past_card_layout.setSpacing(0)

            for i, appt in enumerate(appointments):
                row = AppointmentRow(appt, show_divider=(i > 0))
                row.delete_requested.connect(self._delete_appointment)
                past_card_layout.addWidget(row)

            container_layout.addWidget(past_card)

        layout = self.scrollContent.layout()
        layout.insertWidget(3, container)
        self._past_container = container

    # Lifecycle track 

    def _build_lifecycle_track(self, appt: Appointment) -> QFrame:
        from datetime import timedelta

        appt_date     = _parse_date(appt.appt_date)
        today         = date.today()
        reminder_date = (appt_date - timedelta(days=2)) if appt_date else None
        created_date  = appt_date 

        def _step(icon: str, label: str, sub: str, done: bool, active: bool) -> QVBoxLayout:
            col = QVBoxLayout()
            col.setSpacing(5)
            col.setAlignment(Qt.AlignmentFlag.AlignHCenter)

            circle = QLabel(icon)
            circle.setAlignment(Qt.AlignmentFlag.AlignCenter)
            circle.setFixedSize(30, 30)

            if done:
                circle.setStyleSheet("""
                    QLabel { background: #1A9E78; color: #FFF;
                             font-size: 14px; font-weight: bold;
                             border-radius: 15px; }
                """)
            elif active:
                circle.setStyleSheet("""
                    QLabel { background: #FBDF9E; border: 2px solid #C47B12;
                             border-radius: 15px; font-size: 13px; }
                """)
            else:
                circle.setStyleSheet("""
                    QLabel { background: #FFFFFF; border: 2px solid #C8D9D2;
                             color: #C8D9D2; font-size: 14px; font-weight: bold;
                             border-radius: 15px; }
                """)

            lbl_name = QLabel(label)
            lbl_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_name.setStyleSheet(
                f"font-size: 9px; font-weight: bold; color: {'#7A4D0A' if (done or active) else '#8FA89F'};"
            )

            lbl_sub = QLabel(sub)
            lbl_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_sub.setStyleSheet(
                f"font-size: 9px; color: {'#C47B12' if active else ('#8FA89F' if not done else '#C47B12')};"
                + (" font-weight: 600;" if active else "")
            )

            col.addWidget(circle)
            col.addWidget(lbl_name)
            col.addWidget(lbl_sub)
            return col

        def _connector(done: bool) -> QFrame:
            line = QFrame()
            line.setMinimumWidth(60)
            line.setMaximumHeight(2)
            line.setStyleSheet(
                f"QFrame {{ background: {'#1A9E78' if done else '#C8D9D2'}; margin-bottom: 20px; }}"
            )
            return line

        track = QFrame()
        track.setObjectName("reminderTrack")
        track.setStyleSheet("""
            QFrame#reminderTrack {
                background: #FEF3DC;
                border: 1px solid #FBDF9E;
                border-radius: 14px;
            }
        """)

        outer = QVBoxLayout(track)
        outer.setContentsMargins(20, 16, 20, 16)
        outer.setSpacing(12)

        appt_label = appt_date.strftime("%b %d").upper() if appt_date else ""
        title = QLabel(f"REMINDER LIFECYCLE — {appt_label} APPOINTMENT")
        title.setStyleSheet("font-size: 9px; font-weight: bold; color: #C47B12; letter-spacing: 0.8px;")
        outer.addWidget(title)

        row = QHBoxLayout()
        row.setSpacing(0)

        reminder_active = reminder_date and today >= reminder_date and today < appt_date if appt_date else False
        visit_done      = appt_date and today > appt_date if appt_date else False
        reminder_done   = reminder_date and today > appt_date if appt_date else False

        rem_sub = reminder_date.strftime("%b %d") if reminder_date else "—"
        if reminder_active:
            rem_sub += " ← Today"
        visit_sub = appt_date.strftime("%b %d") if appt_date else "—"

        row.addLayout(_step("✔", "Appt Created", appt_date.strftime("%b %d") if appt_date else "—", done=True,  active=False))
        row.addWidget(_connector(done=True))
        row.addLayout(_step("🔔", "Reminder Flagged", rem_sub,  done=bool(reminder_done), active=bool(reminder_active)))
        row.addWidget(_connector(done=bool(visit_done)))
        row.addLayout(_step("📅", "Visit Day",        visit_sub, done=bool(visit_done),   active=today == appt_date if appt_date else False))
        row.addWidget(_connector(done=bool(visit_done)))
        row.addLayout(_step("✔", "Completed",        "—",       done=bool(visit_done),   active=False))
        row.addStretch()

        outer.addLayout(row)
        return track

    # Add dialog 

    def _open_add_dialog(self):
        dialog = DialogAddAppointment(self.patient_id)
        if dialog.exec():
            self.load_appointments()

    # Delete 

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
