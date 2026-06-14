from datetime import date

from PyQt6 import uic
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QFrame

from models.reminder import Reminder


def fmt_date(value):
    return value.strftime("%B %d, %Y") if value else "—"


class ReminderCard(QFrame):
    clicked = pyqtSignal(object)

    def __init__(self, reminder: Reminder):
        super().__init__()

        uic.loadUi("ui/card_reminder.ui", self)

        self.reminder = reminder

        self.populate(reminder)

    def populate(self, reminder: Reminder):
        self.lblTitle.setText(reminder.title)

        if reminder.subtitle_2:
            self.lblSubtitle.setText(f"{reminder.subtitle} - {reminder.subtitle_2}")
        else:
            self.lblSubtitle.setText(f"{reminder.subtitle}")

        today = date.today()
        days_away = (reminder.schedule_date - today).days

        status = reminder.status.lower()

        if status == "flagged":
            self.lblReminderMessage.show()

            self.lblReminderMessage.setText(
                f"⚠ Flagged today — "
                f"{'scheduled today' if days_away == 0 else f'{days_away} day(s) away'}"
            )

            self.lblReminderMessage.setStyleSheet("""
                QLabel {
                    font-size: 10px;
                    color: #C47B12;
                    font-weight: 600;
                }
            """)

        elif status == "upcoming":
            self.lblReminderMessage.show()

            self.lblReminderMessage.setText(
                f"Reminder will flag on {fmt_date(reminder.remind_on)}"
            )

            self.lblReminderMessage.setStyleSheet("""
                QLabel {
                    font-size: 10px;
                    color: #8FA89F;
                }
            """)

        else:
            self.lblReminderMessage.hide()

        self.lblDates.setText(
            f"Remind on: {fmt_date(reminder.remind_on)}"
            f"  ·  Scheduled: {fmt_date(reminder.schedule_date)}"
        )

        self._apply_status_style(status)

    def _apply_status_style(self, status: str):
        badge_styles = {
            "flagged": (
                "#FBDF9E",
                "#7A4D0A",
                "Flagged"
            ),
            "completed": (
                "#E8F5EB",
                "#1F5C2E",
                "Completed"
            ),
            "dismissed": (
                "#FAE8E8",
                "#8A1F1F",
                "Dismissed"
            ),
            "upcoming": (
                "#EAF3FC",
                "#1A4F8A",
                "Upcoming"
            ),
        }

        bg, fg, text = badge_styles.get(
            status,
            ("#F0F0F0", "#555555", status.title())
        )

        self.lblStatus.setText(text)

        self.lblStatus.setStyleSheet(f"""
            QLabel {{
                background: {bg};
                color: {fg};
                border-radius: 12px;
                padding: 4px 10px;
                font-size: 10px;
                font-weight: bold;
            }}
        """)

        if status == "Flagged":
            self.setStyleSheet("""
                QFrame#ReminderCard {
                    background: #FFFBF0;
                    border-bottom: 1px solid #DDE8E3;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame#ReminderCard {
                    background: white;
                    border-bottom: 1px solid #DDE8E3;
                }
            """)

    def mousePressEvent(self, event):
        self.clicked.emit(self.reminder)
        super().mousePressEvent(event)
