from datetime import date, datetime
import os

from PyQt6.QtWidgets import (
    QWidget, QFrame, QLabel, QHBoxLayout,
    QVBoxLayout, QListWidgetItem, QTableWidgetItem,
    QHeaderView, QSizePolicy, QMessageBox
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon
from PyQt6 import uic

from services.patient_service import PatientService
from services.visit_record_service import VisitRecordService
from services.appointment_service import AppointmentService
from services.vaccination_shot_service import VaccinationShotService
from services.document_service import DocumentService
from services.medical_history_service import MedicalHistoryService
from services.diagnosis_service import DiagnosisService
from services.prescription_service import PrescriptionService
from core.app_settings import AppSettings

from models.patient import Patient
from models.appointment import Appointment
from widgets.reminder_card import reminder_status, compute_remind_on, _parse_date, _fmt_date
from dialogs.dialog_add_record import DialogAddRecord
from dialogs.dialog_add_appointment import DialogAddAppointment


def _fmt_short(value) -> str:
    d = _parse_date(value)
    return d.strftime("%b %d, %Y") if d else "—"


def _bp_status(bp: str | None) -> tuple[str, str]:
    """Return (status_text, color) for a blood pressure string like '120/80'."""
    if not bp:
        return "—", "#8FA89F"
    try:
        parts = bp.replace(" ", "").split("/")
        systolic = int(parts[0])
        if systolic < 120:
            return "Normal", "#1A9E78"
        elif systolic < 130:
            return "Elevated", "#C47B12"
        else:
            return "Watch", "#C47B12"
    except (ValueError, IndexError):
        return bp, "#546860"


class PageDashboard(QWidget):

    def __init__(self):
        super().__init__()
        uic.loadUi("ui/page_dashboard.ui", self)

        self.patient_service      = PatientService()
        self.visit_service        = VisitRecordService()
        self.appointment_service  = AppointmentService()
        self.vaccination_service  = VaccinationShotService()
        self.document_service     = DocumentService()
        self.history_service      = MedicalHistoryService()
        self.diagnosis_service    = DiagnosisService()
        self.prescription_service = PrescriptionService()
        self.settings             = AppSettings()

        self.active_patient = self.patient_service.get_patient_by_code(
            self.settings.get_active_patient_code()
        )
        self.patient_id = self.active_patient.patient_id

        self.btnAddRecord.clicked.connect(self._open_add_record)
        self.btnAddAppt.clicked.connect(self._open_add_appointment)
        self.btnCloseBanner.clicked.connect(self._close_banner)
        self.btnViewAppt.clicked.connect(self._view_flagged_appt)
        self.btnDismissReminder.clicked.connect(self._dismiss_reminder)

        self.load()

    def load(self):
        patient = self.patient_service.get_patient_by_id(self.patient_id)

        hour = datetime.now().hour
        if hour < 12:
            greeting = "Good morning"
        elif hour < 18:
            greeting = "Good afternoon"
        else:
            greeting = "Good evening"
        self.topSub.setText(
            f"{greeting}, {patient.first_name} — here's your health at a glance"
        )

        self._load_stats()
        self._load_reminder_banner()
        self._load_activity()
        self._load_vitals()
        self._load_upcoming_appt()
        self._load_vaccine_progress()

    def _get_icon_path(self, icon_name: str) -> str:
        """Helper to safely point to your project's root assets folder."""
        return os.path.join(os.path.dirname(__file__), '..', 'assets', icon_name)

    #  Stat cards 
    def _load_stats(self):
        today = date.today()

        # Hide the colored icon squares and make the category labels bold + larger
        _icon_names  = ["stat1Icon", "stat2Icon", "stat3Icon", "stat4Icon",
                        "statIcon1", "statIcon2", "statIcon3", "statIcon4"]
        _label_names = ["stat1Label", "stat2Label", "stat3Label", "stat4Label",
                        "statLabel1", "statLabel2", "statLabel3", "statLabel4"]

        from PyQt6.QtWidgets import QFrame, QLabel as _QLabel
        for name in _icon_names:
            w = self.findChild(QFrame, name)
            if w:
                w.hide()

        _label_style = (
            "font-size: 13px; font-weight: bold; color: #546860; letter-spacing: 0.5px;"
        )
        for name in _label_names:
            w = self.findChild(_QLabel, name)
            if w:
                w.setStyleSheet(_label_style)

        records = self.visit_service.get_visit_records_by_patient_id(self.patient_id)
        self.stat1Value.setText(str(len(records)))
        if records:
            latest = max(records, key=lambda r: _parse_date(r.visit_date) or date.min)
            self.stat1Sub.setText(f"Last: {_fmt_short(latest.visit_date)}")
        else:
            self.stat1Sub.setText("No records yet")

        # Vaccinations
        shots = self.vaccination_service.get_vaccinations_by_patient_id(self.patient_id)
        self.stat2Value.setText(str(len(shots)))
        pending = sum(1 for s in shots if s.status == "Pending")
        self.stat2Sub.setText(
            f"{pending} dose{'s' if pending != 1 else ''} pending" if pending else "All up to date"
        )

        # Appointments
        appointments = self.appointment_service.get_appointments_by_patient_id(self.patient_id)
        self.stat3Value.setText(str(len(appointments)))
        upcoming = sorted(
            [a for a in appointments
             if a.status == "Scheduled" and _parse_date(a.appt_date) and _parse_date(a.appt_date) >= today],
            key=lambda a: _parse_date(a.appt_date)
        )
        if upcoming:
            self.stat3Sub.setText(f"Next: {_fmt_short(upcoming[0].appt_date)}")
        else:
            self.stat3Sub.setText("No upcoming")

        # Documents
        record_ids  = {r.record_id for r in records}
        shot_ids    = {s.vaccine_id for s in shots}
        this_month  = 0
        total_docs  = 0
        seen        = set()

        for rid in record_ids:
            for doc in self.document_service.get_documents_by_record_id(rid):
                if doc.doc_id not in seen:
                    seen.add(doc.doc_id)
                    total_docs += 1
                    d = _parse_date(doc.date_uploaded)
                    if d and d.year == today.year and d.month == today.month:
                        this_month += 1

        for vid in shot_ids:
            for doc in self.document_service.get_documents_by_vaccine_id(vid):
                if doc.doc_id not in seen:
                    seen.add(doc.doc_id)
                    total_docs += 1
                    d = _parse_date(doc.date_uploaded)
                    if d and d.year == today.year and d.month == today.month:
                        this_month += 1

        self.stat4Value.setText(str(total_docs))
        self.stat4Sub.setText(
            f"{this_month} linked this month" if this_month else "No new this month"
        )

    # Reminder banner 

    def _load_reminder_banner(self):
        today        = date.today()
        appointments = self.appointment_service.get_appointments_by_patient_id(self.patient_id)
        flagged      = [a for a in appointments if reminder_status(a) == "flagged"]

        if not flagged:
            self.reminderBanner.hide()
            self._flagged_appt = None
            return

        appt      = sorted(flagged, key=lambda a: _parse_date(a.appt_date) or today)[0]
        self._flagged_appt = appt

        appt_date = _parse_date(appt.appt_date)
        days_away = (appt_date - today).days if appt_date else None

        self.bannerEyebrow.setText(
            f"APPOINTMENT REMINDER — FLAGGED TODAY"
        )

        if days_away == 0:
            title = f"Your appointment at {appt.clinic_name} is today"
        elif days_away == 1:
            title = f"Your appointment at {appt.clinic_name} is tomorrow"
        else:
            title = f"Your appointment at {appt.clinic_name} is in {days_away} days"

        self.bannerTitle.setText(title)
        self.bannerSub.setText(
            f"{_fmt_short(appt.appt_date)}  ·  {appt.appt_time}  ·  "
            f"{appt.clinic_name} — {appt.purpose}"
        )
        self.reminderBanner.show()

    #  Recent activity 

    def _load_activity(self):
        self.activityList.clear()
        items = []

        # Visit records - Removed [Rec] emoji mapping
        records = self.visit_service.get_visit_records_by_patient_id(self.patient_id)
        for r in records:
            diagnoses = self.diagnosis_service.get_diagnoses_by_record_id(r.record_id)
            dx_text = ", ".join(d.diagnosis_name for d in diagnoses) or "Visit"
            items.append((_parse_date(r.visit_date), f"{dx_text}  ·  {_fmt_short(r.visit_date)}", "description.svg"))

        # Vaccinations - Removed [Vax] emoji mapping
        shots = self.vaccination_service.get_vaccinations_by_patient_id(self.patient_id)
        for s in shots:
            items.append((_parse_date(s.date_administered),
                          f"{s.vaccination_name} Dose {s.dose_number}  ·  {_fmt_short(s.date_administered)}", "vaccines.svg"))

        # Appointments - Removed [Cal] and [!] emoji mappings
        appointments = self.appointment_service.get_appointments_by_patient_id(self.patient_id)
        for a in appointments:
            items.append((_parse_date(a.appt_date),
                          f"{a.purpose}  ·  {_fmt_short(a.appt_date)}", "calendar_month.svg"))
            remind_on = compute_remind_on(a.appt_date)
            if remind_on:
                items.append((remind_on,
                               f"Reminder for {a.purpose}  ·  Remind: {_fmt_short(remind_on)}", "notifications.svg"))

        items.sort(key=lambda x: x[0] or date.min, reverse=True)
        for _, text, icon_name in items[:8]:
            item = QListWidgetItem(text)
            icon_path = self._get_icon_path(icon_name)
            if os.path.exists(icon_path):
                item.setIcon(QIcon(icon_path))
            self.activityList.addItem(item)

        if not items:
            self.activityList.addItem(QListWidgetItem("No activity yet."))

    #  Latest vitals 

    def _load_vitals(self):
        records = self.visit_service.get_visit_records_by_patient_id(self.patient_id)

        if not records:
            self.vitalsDate.setText("No records")
            self.vitalsTable.setRowCount(1)
            self.vitalsTable.setColumnCount(1)
            self.vitalsTable.setItem(0, 0, QTableWidgetItem("No visit records found."))
            return

        latest = max(records, key=lambda r: _parse_date(r.visit_date) or date.min)
        self.vitalsDate.setText(_fmt_short(latest.visit_date))

        diagnoses     = self.diagnosis_service.get_diagnoses_by_record_id(latest.record_id)
        prescriptions = self.prescription_service.get_prescriptions_by_record_id(latest.record_id)

        rows = []

        # BP
        bp_status, bp_color = _bp_status(latest.blood_pressure)
        rows.append(("Blood Pressure", latest.blood_pressure or "—", bp_status, bp_color))

        # Weight
        if latest.weight_kg:
            rows.append(("Weight", f"{latest.weight_kg} kg", "Recorded", "#1A9E78"))

        # Diagnoses
        for d in diagnoses:
            rows.append(("Diagnosis", d.diagnosis_name, "", "#546860"))

        # Prescriptions
        for p in prescriptions:
            rows.append(("Prescription", f"{p.medication_name} {p.dosage}".strip(), "", "#546860"))

        self.vitalsTable.setRowCount(len(rows))
        self.vitalsTable.setColumnCount(3)
        self.vitalsTable.horizontalHeader().hide()
        self.vitalsTable.verticalHeader().hide()
        self.vitalsTable.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )
        self.vitalsTable.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.vitalsTable.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.ResizeToContents
        )

        for i, (label, value, status, color) in enumerate(rows):
            item_label = QTableWidgetItem(label)
            item_label.setForeground(__import__('PyQt6.QtGui', fromlist=['QColor']).QColor("#8FA89F"))
            item_value = QTableWidgetItem(value)
            item_status = QTableWidgetItem(status)
            item_status.setForeground(__import__('PyQt6.QtGui', fromlist=['QColor']).QColor(color))
            self.vitalsTable.setItem(i, 0, item_label)
            self.vitalsTable.setItem(i, 1, item_value)
            self.vitalsTable.setItem(i, 2, item_status)

        self.vitalsTable.resizeRowsToContents()

    #  Upcoming appointment card 

    def _load_upcoming_appt(self):
        today        = date.today()
        appointments = self.appointment_service.get_appointments_by_patient_id(self.patient_id)
        upcoming     = sorted(
            [a for a in appointments
             if a.status == "Scheduled" and _parse_date(a.appt_date) and _parse_date(a.appt_date) >= today],
            key=lambda a: _parse_date(a.appt_date)
        )

        if not upcoming:
            self.apptDay.setText("—")
            self.apptMonth.setText("")
            self.apptDoctor.setText("No upcoming appointments")
            self.apptNote.setText("")
            self.apptRemind.setText("")
            self.apptTime.setText("")
            return

        appt      = upcoming[0]
        appt_date = _parse_date(appt.appt_date)
        remind_on = compute_remind_on(appt_date)

        self.apptDay.setText(appt_date.strftime("%d") if appt_date else "—")
        self.apptMonth.setText(appt_date.strftime("%b %Y").upper() if appt_date else "")
        self.apptDoctor.setText(appt.clinic_name)
        self.apptNote.setText(f"{appt.purpose}")
        self.apptRemind.setText(
            f"Reminder set: {remind_on.strftime('%b %d') if remind_on else '—'}"
        )
        self.apptTime.setText(str(appt.appt_time))

    # Vaccine progress card 

    def _load_vaccine_progress(self):
        shots = self.vaccination_service.get_vaccinations_by_patient_id(self.patient_id)

        groups: dict[str, list] = {}
        for s in shots:
            key = s.vaccination_name.strip().lower()
            groups.setdefault(key, []).append(s)

        if hasattr(self, "_vacc_container"):
            self._vacc_container.deleteLater()

        from PyQt6.QtWidgets import QWidget as _W
        container = _W()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        if not groups:
            empty = QLabel("No vaccinations logged yet.")
            empty.setStyleSheet("font-size: 12px; color: #8FA89F; padding: 14px 20px;")
            layout.addWidget(empty)
        else:
            entries = list(groups.values())[:3] 
            for i, group_shots in enumerate(entries):
                name     = group_shots[0].vaccination_name
                total    = max(s.dose_number for s in group_shots)
                done     = sum(1 for s in group_shots if s.status == "Completed")
                complete = done >= total

                row = QHBoxLayout()
                row.setContentsMargins(20, 12, 20, 12)
                row.setSpacing(12)

                # Replaced raw [Vax] text label layout with dynamic QPixmap lookup
                icon = QLabel()
                icon.setFixedSize(36, 36)
                icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
                color = "#E8F5EB" if complete else "#E3F5EE"
                icon.setStyleSheet(f"QLabel {{ background: {color}; border-radius: 9px; padding: 4px; }}")
                
                icon_path = self._get_icon_path("vaccines.svg")
                if os.path.exists(icon_path):
                    pixmap = QIcon(icon_path).pixmap(QSize(20, 20))
                    icon.setPixmap(pixmap)

                row.addWidget(icon)

                info = QVBoxLayout()
                info.setSpacing(2)
                lbl_name = QLabel(name)
                lbl_name.setStyleSheet("font-size: 12px; font-weight: bold; color: #1C2B25;")
                meta_text = f"{'Single dose' if total == 1 else f'{total}-dose series'}  ·  {'Complete' if complete else f'Dose {done} done'}"
                lbl_meta = QLabel(meta_text)
                lbl_meta.setStyleSheet("font-size: 10px; color: #546860;")

                pip_row = QHBoxLayout()
                pip_row.setSpacing(3)
                for p in range(total):
                    pip = QFrame()
                    pip.setFixedSize(20, 6)
                    pip.setStyleSheet(
                        f"QFrame {{ background: {'#1A9E78' if p < done else '#C8D9D2'}; border-radius: 3px; }}"
                    )
                    pip_row.addWidget(pip)
                pip_row.addStretch()

                info.addWidget(lbl_name)
                info.addWidget(lbl_meta)
                info.addLayout(pip_row)
                row.addLayout(info)

                row_widget = QWidget()
                row_widget.setLayout(row)
                layout.addWidget(row_widget)

                if i < len(entries) - 1:
                    div = QFrame()
                    div.setFrameShape(QFrame.Shape.HLine)
                    div.setStyleSheet("QFrame { color: #DDE8E3; margin: 0 20px; }")
                    layout.addWidget(div)

        card_layout = self.cardVaccine.layout()
        card_layout.insertWidget(2, container)
        self._vacc_container = container

    #  Actions 

    def _open_add_record(self):
        dialog = DialogAddRecord(self.patient_id)
        if dialog.exec():
            self.load()

    def _open_add_appointment(self):
        dialog = DialogAddAppointment(self.patient_id)
        if dialog.exec():
            self.load()

    def _close_banner(self):
        self.reminderBanner.hide()

    def _view_flagged_appt(self):
        if not hasattr(self, "_flagged_appt") or not self._flagged_appt:
            return
        appt = self._flagged_appt
        remind_on = compute_remind_on(appt.appt_date)
        QMessageBox.information(
            self,
            "Appointment Details",
            f"Purpose:    {appt.purpose}\n"
            f"Clinic:     {appt.clinic_name}\n"
            f"Date:       {_fmt_short(appt.appt_date)}\n"
            f"Time:       {appt.appt_time}\n"
            f"Status:     {appt.status}\n"
            f"Remind on:  {_fmt_short(remind_on)}\n"
            f"Code:       {appt.appointment_code}"
        )

    def _dismiss_reminder(self):
        if not hasattr(self, "_flagged_appt") or not self._flagged_appt:
            return
        appt = self._flagged_appt
        reply = QMessageBox.question(
            self,
            "Mark as Prepared",
            f"Mark the appointment for '{appt.purpose}' as prepared?\n\n"
            "This will mark the appointment as Completed.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        self.appointment_service.update_appointment(
            appointment_id=appt.appointment_id,
            appt_date=appt.appt_date,
            appt_time=appt.appt_time,
            purpose=appt.purpose,
            clinic_name=appt.clinic_name,
            status="Completed",
            patient_id=appt.patient_id
        )
        self.load()