from datetime import date

from PyQt6.QtWidgets import (
    QWidget, QFrame, QLabel, QHBoxLayout,
    QVBoxLayout, QPushButton, QMessageBox,
    QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6 import uic

from services.appointment_service import AppointmentService
from services.patient_service import PatientService
from core.app_settings import AppSettings
from models.appointment import Appointment
from widgets.reminder_card import reminder_status, compute_remind_on, _parse_date, _fmt_date, ReminderCard


class PageReminders(QWidget):

    def __init__(self):
        super().__init__()
        uic.loadUi("ui/page_reminders.ui", self)

        self.appointment_service = AppointmentService()
        self.patient_service     = PatientService()
        self.settings            = AppSettings()

        self.active_patient = self.patient_service.get_patient_by_code(
            self.settings.get_active_patient_code()
        ) if self.settings.get_active_patient_code() else None
        self.patient_id = self.active_patient.patient_id if self.active_patient else None

        self.load_reminders()

    def load_reminders(self):
        if not self.patient_id:
            return
        appointments = self.appointment_service.get_appointments_by_patient_id(
            self.patient_id
        )

        today = date.today()

        flagged   = []
        upcoming  = []
        completed = []
        dismissed = []

        for appt in appointments:
            s = reminder_status(appt)
            if s == "flagged":
                flagged.append(appt)
            elif s == "upcoming":
                upcoming.append(appt)
            elif s == "completed":
                completed.append(appt)
            else:
                dismissed.append(appt)

        flagged.sort(key=lambda a: _parse_date(a.appt_date) or today)
        upcoming.sort(key=lambda a: _parse_date(a.appt_date) or today)
        completed.sort(key=lambda a: _parse_date(a.appt_date) or today, reverse=True)

        all_reminders = flagged + upcoming + completed + dismissed

        self._populate_banner(flagged)
        self._populate_list(all_reminders)

    def _populate_banner(self, flagged: list[Appointment]):
        if hasattr(self, "_banner_widget"):
            self._banner_widget.deleteLater()
            del self._banner_widget

        self.activeBanner.hide()

        if not flagged:
            return

        appt      = flagged[0]
        appt_date = _parse_date(appt.appt_date)
        today     = date.today()
        days_away = (appt_date - today).days if appt_date else None

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

        bell = QLabel("[!]")
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
        lbl_eyebrow = QLabel(f"REMINDER FLAGGED — TODAY IS {today_str}")
        lbl_eyebrow.setStyleSheet(
            "font-size: 9px; font-weight: bold; color: #C47B12; letter-spacing: 0.8px;"
        )
        info.addWidget(lbl_eyebrow)

        if days_away == 0:
            body = "Your appointment is today"
        elif days_away == 1:
            body = "Prepare for your visit tomorrow"
        else:
            body = f"Prepare for your visit in {days_away} days"

        lbl_body = QLabel(body)
        lbl_body.setStyleSheet("font-size: 14px; font-weight: bold; color: #3D2800;")
        info.addWidget(lbl_body)

        detail = f"{_fmt_date(appt_date)}  ·  {appt.appt_time}  ·  {appt.clinic_name}"
        lbl_detail = QLabel(detail)
        lbl_detail.setStyleSheet("font-size: 11px; color: #7A4D0A;")
        info.addWidget(lbl_detail)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        btn_view = QPushButton("View Details")
        btn_view.setStyleSheet("""
            QPushButton {
                background: #C47B12; color: #FFF;
                font-size: 11px; font-weight: 600;
                border: none; border-radius: 6px;
                padding: 6px 14px;
            }
            QPushButton:hover { background: #7A4D0A; }
        """)
        btn_view.clicked.connect(lambda: self._show_detail(appt))

        btn_dismiss = QPushButton("Dismiss")
        btn_dismiss.setStyleSheet("""
            QPushButton {
                background: rgba(196,123,18,0.12); color: #7A4D0A;
                font-size: 11px; font-weight: 600;
                border: none; border-radius: 6px;
                padding: 6px 14px;
            }
            QPushButton:hover { background: rgba(196,123,18,0.22); }
        """)
        btn_dismiss.clicked.connect(lambda: self._dismiss(appt))

        btn_row.addWidget(btn_view)
        btn_row.addWidget(btn_dismiss)
        btn_row.addStretch()
        info.addLayout(btn_row)

        layout.addLayout(info)

        self.scrollContent.layout().insertWidget(0, banner)
        self._banner_widget = banner

    def _populate_list(self, appointments: list[Appointment]):
        if hasattr(self, "_list_container"):
            self._list_container.deleteLater()


        self.remList.hide()

        if not appointments:
            empty = QLabel("No reminders yet. Add an appointment to get started.")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setStyleSheet("font-size: 13px; color: #8FA89F; padding: 20px 0;")
            idx = 2 if hasattr(self, "_banner_widget") else 1
            self.scrollContent.layout().insertWidget(idx, empty)
            self._list_container = empty
            return

        list_frame = QFrame()
        list_frame.setObjectName("remListDyn")
        list_frame.setStyleSheet("""
            QFrame#remListDyn {
                background: #FFFFFF;
                border: 1px solid #DDE8E3;
                border-radius: 14px;
            }
        """)
        list_layout = QVBoxLayout(list_frame)
        list_layout.setContentsMargins(0, 0, 0, 0)
        list_layout.setSpacing(0)

        for i, appt in enumerate(appointments):
            show_div = (i < len(appointments) - 1)
            card = ReminderCard(appt, show_divider=show_div)
            card.view_clicked.connect(self._show_detail)
            list_layout.addWidget(card)

        idx = 2 if hasattr(self, "_banner_widget") else 1
        self.scrollContent.layout().insertWidget(idx, list_frame)
        self._list_container = list_frame

    def _show_detail(self, appt: Appointment):
        from widgets.reminder_card import compute_remind_on, _fmt_date
        remind_on = compute_remind_on(appt.appt_date)

        QMessageBox.information(
            self,
            "Appointment Details",
            f"Purpose:     {appt.purpose}\n"
            f"Clinic:      {appt.clinic_name}\n"
            f"Date:        {_fmt_date(appt.appt_date)}\n"
            f"Time:        {appt.appt_time}\n"
            f"Status:      {appt.status}\n"
            f"Remind on:   {_fmt_date(remind_on)}\n"
            f"Code:        {appt.appointment_code}"
        )

    def _dismiss(self, appt: Appointment):
        reply = QMessageBox.question(
            self,
            "Dismiss Reminder",
            f"Dismiss the reminder for '{appt.purpose}' on {_fmt_date(appt.appt_date)}?\n\n"
            "This will mark the appointment as Cancelled.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        from services.appointment_service import AppointmentService
        svc = AppointmentService()
        svc.update_appointment(
            appointment_id=appt.appointment_id,
            appt_date=appt.appt_date,
            appt_time=appt.appt_time,
            purpose=appt.purpose,
            clinic_name=appt.clinic_name,
            status="Cancelled",
            patient_id=appt.patient_id
        )

        self.load_reminders()