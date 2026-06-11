import os
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QBrush
import sys
from datetime import date

from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QApplication, QWidget, QMessageBox
from PyQt6 import uic
from PyQt6.QtCore import QSize, Qt

from database.init_db import init_db
from core.app_settings import AppSettings
from services.patient_service import PatientService
from services.visit_record_service import VisitRecordService
from services.appointment_service import AppointmentService
from services.vaccination_shot_service import VaccinationShotService
from services.document_service import DocumentService
from services.diagnosis_service import DiagnosisService

from pages.page_dashboard import PageDashboard
from pages.page_profile import PageProfile
from pages.page_records import PageRecords
from pages.page_vaccination import PageVaccinations
from pages.page_appointments import PageAppointments
from pages.page_reminder import PageReminders
from pages.page_documents import PageDocuments

from widgets.reminder_card import reminder_status, _parse_date


class MainWindow(QMainWindow):
    def __init__(self, user=None):
        super().__init__()
        self._logged_in_user = user
        uic.loadUi("ui/main_window.ui", self)

        icon_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'logo.png')
        
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            fallback_path = os.path.join(os.path.dirname(__file__), 'assets', 'logo.png')
            self.setWindowIcon(QIcon(fallback_path))

        self.setWindowTitle("HealthLink — Digital Health Record")

        self.apply_navigation_icons()

        self.centralWidget.setStyleSheet("background-color: #2B8F74;")
        self.stackedWidget.setStyleSheet("background-color: #F2F7F5;")

        pages = [
            self.pageDashboard, self.pageAppointments, self.pageVaccinations,
            self.pageRecords, self.pageProfile, self.pageDocuments, self.pageReminders
        ]
        
        for page in pages:
            page.setStyleSheet("background-color: #F2F7F5;")

        layout = self.centralWidget.layout()
 
        layout.setStretch(0, 0)
        layout.setStretch(1, 1) 
    
    def load_icon(self, button, icon_name):
        icon_path = os.path.join(os.path.dirname(__file__), '..', 'assets', icon_name)
        
        if os.path.exists(icon_path):
            button.setIcon(QIcon(icon_path))
            button.setIconSize(QSize(20, 20))
        
        else:
            print(f"Warning: Icon not found at {icon_path}")
      
    def apply_navigation_icons(self):
        self.load_icon(self.navDashboard, "dashboard.svg")
        self.load_icon(self.navProfile, "account_circle.svg")
        self.load_icon(self.navRecords, "record.svg")
        self.load_icon(self.navVaccinations, "vaccines.svg")
        self.load_icon(self.navAppointments, "calendar_month.svg")
        self.load_icon(self.navReminders, "notifications.svg")
        self.load_icon(self.navDocuments, "document.svg")
        self.load_icon(self.logOutBtn, "ic_logout.svg")

        logo_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'logo.png')
        if os.path.exists(logo_path):
            from PyQt6.QtGui import QPixmap
            self.logoIcon.setPixmap(QPixmap(logo_path).scaled(
                36, 36,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            ))

        self.settings        = AppSettings()
        self.patient_service = PatientService()

        patient_code = None
        if self._logged_in_user and self._logged_in_user.patient_code:
            patient_code = self._logged_in_user.patient_code
            self.settings.set_active_patient_code(patient_code)
        elif self.settings.get_active_patient_code():
            patient_code = self.settings.get_active_patient_code()

        self.active_patient = (
            self.patient_service.get_patient_by_code(patient_code)
            if patient_code else None
        )

        self.page_dashboard    = PageDashboard()
        self.page_profile      = PageProfile()
        self.page_records      = PageRecords()
        self.page_vaccinations = PageVaccinations()
        self.page_appointments = PageAppointments()
        self.page_reminders    = PageReminders()
        self.page_documents    = PageDocuments()

        self.page_dashboard.navigate_requested.connect(self._navigate)

        self._embed(self.pageDashboard,    self.page_dashboard)
        self._embed(self.pageProfile,      self.page_profile)
        self._embed(self.pageRecords,      self.page_records)
        self._embed(self.pageVaccinations, self.page_vaccinations)
        self._embed(self.pageAppointments, self.page_appointments)
        self._embed(self.pageReminders,    self.page_reminders)
        self._embed(self.pageDocuments,    self.page_documents)

        self._nav_buttons = [
            self.navDashboard,
            self.navProfile,
            self.navRecords,
            self.navVaccinations,
            self.navAppointments,
            self.navReminders,
            self.navDocuments,
        ]

        self._pages = [
            self.pageDashboard,
            self.pageProfile,
            self.pageRecords,
            self.pageVaccinations,
            self.pageAppointments,
            self.pageReminders,
            self.pageDocuments,
        ]

        self.navDashboard.clicked.connect(
            lambda: self._navigate(0))
        self.navProfile.clicked.connect(
            lambda: self._navigate(1))
        self.navRecords.clicked.connect(
            lambda: self._navigate(2))
        self.navVaccinations.clicked.connect(
            lambda: self._navigate(3))
        self.navAppointments.clicked.connect(
            lambda: self._navigate(4))
        self.navReminders.clicked.connect(
            lambda: self._navigate(5))
        self.navDocuments.clicked.connect(
            lambda: self._navigate(6))

        self.logOutBtn.clicked.connect(self._logout)
        self.patientChip.hide()

        self._load_patient_chip()

        self._update_badges()
        self._navigate(0)

    def _embed(self, slot_widget, page_widget):
        layout = slot_widget.layout()
        if layout is None:
            layout = QVBoxLayout(slot_widget)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
        
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        
        layout.addWidget(page_widget)
        page_widget.show()


    def _navigate(self, index: int):
        self.stackedWidget.setCurrentIndex(index) 
        for i, btn in enumerate(self._nav_buttons):
            btn.setChecked(i == index)
        self._update_badges()


    def _load_patient_chip(self):
        p = self.active_patient
        if not p:
            if self._logged_in_user:
                full_name = f"{self._logged_in_user.first_name} {self._logged_in_user.last_name}"
                self.patientName.setText(full_name)
                self.patientId.setText("No profile yet")
                initials = f"{self._logged_in_user.first_name[0]}{self._logged_in_user.last_name[0]}".upper()
                self.patientAvatar.setText(initials)
            return

        full_name = f"{p.first_name} {p.last_name}"
        initials  = f"{p.first_name[0]}{p.last_name[0]}".upper()

        self.patientName.setText(full_name)
        self.patientId.setText(p.patient_code)

        photo_path = os.path.join(os.path.dirname(__file__), 'assets', f"{p.patient_code}.png")

        if os.path.exists(photo_path):
            size = 48
            raw = QPixmap(photo_path).scaled(
                size, size,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )
            circular = QPixmap(size, size)
            circular.fill(Qt.GlobalColor.transparent)
            painter = QPainter(circular)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setBrush(QBrush(raw))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(0, 0, size, size)
            painter.end()

            self.patientAvatar.setPixmap(circular)
            self.patientAvatar.setText("")
        else:
            self.patientAvatar.setText(initials)


    def _update_badges(self):
        if not self.active_patient:
            return
        patient_id = self.active_patient.patient_id
        today      = date.today()

        records = VisitRecordService().get_visit_records_by_patient_id(patient_id)
        self._set_badge(self.badgeRecords, len(records))

        shots = VaccinationShotService().get_vaccinations_by_patient_id(patient_id)
        self._set_badge(self.badgeVaccinations, len(shots))

        appointments = AppointmentService().get_appointments_by_patient_id(patient_id)
        upcoming = [
            a for a in appointments
            if a.status == "Scheduled" and _parse_date(a.appt_date) and _parse_date(a.appt_date) >= today
        ]
        self._set_badge(self.badgeAppointments, len(upcoming))

        flagged = [a for a in appointments if reminder_status(a) == "flagged"]
        self._set_badge(self.badgeReminders, len(flagged), amber=bool(flagged))

        record_ids = {r.record_id for r in records}
        shot_ids   = {s.vaccine_id for s in shots}
        doc_svc    = DocumentService()
        seen       = set()
        for rid in record_ids:
            for d in doc_svc.get_documents_by_record_id(rid):
                seen.add(d.doc_id)
        for vid in shot_ids:
            for d in doc_svc.get_documents_by_vaccine_id(vid):
                seen.add(d.doc_id)
        self._set_badge(self.badgeDocuments, len(seen))

    def _set_badge(self, badge_label, count: int, amber: bool = False):
        if count == 0:
            badge_label.hide()
            return
        badge_label.setText(str(count))
        badge_label.show()
        color = "#E8830A" if amber else "#1A9E78"
        badge_label.setStyleSheet(f"""
            QLabel {{
                background: {color};
                color: #FFF;
                font-size: 10px;
                font-weight: bold;
                border-radius: 10px;
            }}
        """)

    def _logout(self):
        reply = QMessageBox.question(
            self, "Log Out",
            "Are you sure you want to log out?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            from core.app_settings import AppSettings
            AppSettings().set_active_patient_code("")
            from login_window import AuthWindow
            self.auth_window = AuthWindow()
            self.auth_window.show()
            self.close()

def main():
    init_db()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()