from datetime import date, datetime, timedelta

from PyQt6.QtWidgets import (
    QFrame, QLabel, QHBoxLayout, QVBoxLayout,
    QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QMouseEvent

from models.appointment import Appointment


def _parse_date(value) -> date | None:
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            return None
    return None


def _fmt_date(value) -> str:
    d = _parse_date(value)
    return d.strftime("%B %d, %Y") if d else "—"


def compute_remind_on(appt_date) -> date | None:
    d = _parse_date(appt_date)
    return (d - timedelta(days=2)) if d else None


def reminder_status(appt: Appointment) -> str:
    appt_date   = _parse_date(appt.appt_date)
    remind_on   = compute_remind_on(appt_date)
    today       = date.today()

    if appt.status == "Cancelled":
        return "dismissed"
    if appt.status == "Completed":
        return "completed"
    if appt_date and today > appt_date:
        return "flagged"
    if remind_on and today >= remind_on:
        return "flagged"
    return "upcoming"


class ReminderCard(QFrame):

    clicked = pyqtSignal(object)

    def __init__(self, appt: Appointment, show_divider: bool = True):
        super().__init__()
        self.appt = appt

        status      = reminder_status(appt)
        appt_date   = _parse_date(appt.appt_date)
        remind_on   = compute_remind_on(appt_date)
        today       = date.today()

        days_away   = (appt_date - today).days if appt_date else None

        obj_name = f"remCard_{id(self)}"
        self.setObjectName(obj_name)

        border = "border-bottom: 1px solid #DDE8E3;" if show_divider else ""
        self.setStyleSheet(f"""
            QFrame#{obj_name} {{
                background: transparent;
                {border}
            }}
            QFrame#{obj_name}:hover {{
                background: #F8FBFA;
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(14)

        info = QVBoxLayout()
        info.setSpacing(3)

        lbl_title = QLabel(appt.purpose)
        lbl_title.setStyleSheet("font-size: 13px; font-weight: bold; color: #1C2B25;")
        info.addWidget(lbl_title)

        lbl_meta = QLabel(f"{appt.clinic_name}  ·  {appt.appt_time}")
        lbl_meta.setStyleSheet("font-size: 11px; color: #546860;")
        info.addWidget(lbl_meta)

        lbl_dates = QLabel(
            f"remind_on: {_fmt_date(remind_on)}   ·   "
            f"appointment_date: {_fmt_date(appt_date)}"
        )
        lbl_dates.setStyleSheet("font-size: 10px; color: #8FA89F; font-style: italic;")
        info.addWidget(lbl_dates)

        layout.addLayout(info)
        layout.addStretch()

        right = QVBoxLayout()
        right.setSpacing(8)
        right.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        badge_styles = {
            "flagged":   ("#FBDF9E", "#7A4D0A", "Flagged"),
            "completed": ("#E8F5EB", "#1F5C2E", "Completed"),
            "dismissed": ("#FAE8E8", "#8A1F1F", "Dismissed"),
            "upcoming":  ("#EAF3FC", "#1A4F8A", "Upcoming"),
        }
        bg, fg, label = badge_styles.get(status, ("#F0F0F0", "#555", status.title()))

        badge = QLabel(f"  {label}  ")
        badge.setAlignment(Qt.AlignmentFlag.AlignRight)
        badge.setStyleSheet(f"""
            QLabel {{
                background: {bg};
                color: {fg};
                font-size: 10px;
                font-weight: bold;
                border-radius: 20px;
                padding: 2px 4px;
            }}
        """)
        badge.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        right.addWidget(badge)
        layout.addLayout(right)

    def mousePressEvent(self, event: QMouseEvent):
        self.clicked.emit(self.appt)
        super().mousePressEvent(event)
