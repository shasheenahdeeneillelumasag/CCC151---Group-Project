from datetime import date, datetime
import os

from PyQt6.QtWidgets import (
    QWidget, QFrame, QLabel, QHBoxLayout,
    QVBoxLayout, QListWidgetItem, QTableWidgetItem,
    QHeaderView, QMessageBox
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6 import uic

from services.container import *
from core.app_settings import AppSettings

from widgets.reminder_card import reminder_status, compute_remind_on, _parse_date



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

    navigate_requested = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        uic.loadUi("ui/page_dashboard.ui", self)

        self.patient_service      = patient_service
        self.visit_service        = visit_record_service
        self.appointment_service  = appointment_service
        self.vaccination_service  = vaccination_shot_service
        self.document_service     = document_service
        self.history_service      = medical_history_service
        self.diagnosis_service    = diagnosis_service
        self.prescription_service = prescription_service
        self.settings             = AppSettings()

        self.active_patient = self.patient_service.get_patient_by_code(
            self.settings.get_active_patient_code()
        ) if self.settings.get_active_patient_code() else None
        self.patient_id = self.active_patient.patient_id if self.active_patient else None
        self.btnViewVacc.clicked.connect(lambda: self.navigate_requested.emit(3))

        self._make_stat_cards_clickable()


        self.patient_service.changed.connect(self.load)
        self.visit_service.changed.connect(self.load)
        self.vaccination_service.changed.connect(self.load)
        self.appointment_service.changed.connect(self.load)

        self.load()

    def _make_stat_cards_clickable(self):
        for card, page_idx in [
            ("statCard1", 2),
            ("statCard2", 3),
            ("statCard3", 4),
            ("statCard4", 6),
        ]:
            frame = self.findChild(QFrame, card)
            if frame:
                frame.setCursor(Qt.CursorShape.PointingHandCursor)
                frame.mousePressEvent = lambda e, idx=page_idx: self.navigate_requested.emit(idx)

    def _refresh_patient(self):
        self.active_patient = self.patient_service.get_patient_by_code(
            self.settings.get_active_patient_code()
        ) if self.settings.get_active_patient_code() else None
        new_id = self.active_patient.patient_id if self.active_patient else None
        if new_id != self.patient_id:
            self.patient_id = new_id

    def load(self):
        self._refresh_patient()
        if not self.patient_id:
            return
        patient = self.patient_service.get_patient_by_id(self.patient_id)

        hour = datetime.now().hour
        if hour < 12:
            greeting = "Good morning"
        elif hour < 18:
            greeting = "Good afternoon"
        else:
            greeting = "Good evening"


        self._load_stats()
        self._load_activity()
        self._load_vitals()
        self._load_upcoming_appt()
        self._load_vaccine_progress()

    def _get_icon_path(self, icon_name: str) -> str:
        return os.path.join(os.path.dirname(__file__), '..', 'assets', icon_name)

    def _load_stats(self):
        today = date.today()

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

        shots = self.vaccination_service.get_vaccinations_by_patient_id(self.patient_id)
        self.stat2Value.setText(str(len(shots)))
        pending = sum(1 for s in shots if s.status == "Pending")
        self.stat2Sub.setText(
            f"{pending} dose{'s' if pending != 1 else ''} pending" if pending else "All up to date"
        )

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

    def _load_activity(self):
        self.activityList.clear()
        items = []

        records = self.visit_service.get_visit_records_by_patient_id(self.patient_id)
        for r in records:
            diagnoses = self.diagnosis_service.get_diagnoses_by_record_id(r.record_id)
            dx_text = ", ".join(d.diagnosis_name for d in diagnoses) or "Visit"
            items.append((_parse_date(r.visit_date), f"{dx_text}  ·  {_fmt_short(r.visit_date)}", "description.svg"))

        shots = self.vaccination_service.get_vaccinations_by_patient_id(self.patient_id)
        for s in shots:
            items.append((_parse_date(s.display_date),
                          f"{s.vaccination_name} Dose {s.display_dose}  ·  {_fmt_short(s.display_date)}", "vaccines.svg"))

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

    def _load_vitals(self):
        records = self.visit_service.get_visit_records_by_patient_id(self.patient_id)

        if not records:
            self.vitalsTable.hide()
            self._vitals_empty.show() if hasattr(self, "_vitals_empty") else None
            if not hasattr(self, "_vitals_empty"):
                from PyQt6.QtWidgets import QLabel as _EmptyLabel
                self._vitals_empty = _EmptyLabel("No visit records found.")
                self._vitals_empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self._vitals_empty.setStyleSheet(
                    "font-size: 12px; color: #8FA89F; padding: 30px 20px;"
                )
                self.cardVitals.layout().addWidget(self._vitals_empty)
            return

        self.vitalsTable.show()
        if hasattr(self, "_vitals_empty"):
            self._vitals_empty.hide()

        latest = max(records, key=lambda r: _parse_date(r.visit_date) or date.min)

        diagnoses     = self.diagnosis_service.get_diagnoses_by_record_id(latest.record_id)
        prescriptions = self.prescription_service.get_prescriptions_by_record_id(latest.record_id)

        rows = []

        bp_status, bp_color = _bp_status(latest.blood_pressure)
        rows.append(("Blood Pressure", latest.blood_pressure or "—", bp_status, bp_color))

        if latest.weight_kg is not None:
            rows.append(("Weight", f"{latest.weight_kg} kg", "Recorded", "#1A9E78"))

        for d in diagnoses:
            rows.append(("Diagnosis", d.diagnosis_name, "", "#546860"))

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

    def _load_upcoming_appt(self):
        today        = date.today()
        appointments = self.appointment_service.get_appointments_by_patient_id(self.patient_id)
        upcoming     = sorted(
            [a for a in appointments
             if a.status == "Scheduled" and _parse_date(a.appt_date) and _parse_date(a.appt_date) >= today],
            key=lambda a: _parse_date(a.appt_date)
        )

        if not upcoming:
            self.apptDay.hide()
            self.apptMonth.hide()
            self.apptDoctor.setStyleSheet("font-size: 12px; color: #8FA89F; padding: 14px 20px;")
            self.apptDoctor.setText("No upcoming appointments")
            self.apptNote.setText("")
            self.apptTime.setText("")
            return
        self.apptDay.show()
        self.apptMonth.show()
        self.apptDoctor.setStyleSheet("font-size: 13px; font-weight: bold; color: #1C2B25;")

        appt      = upcoming[0]
        appt_date = _parse_date(appt.appt_date)

        self.apptDay.setText(appt_date.strftime("%d") if appt_date else "—")
        self.apptMonth.setText(appt_date.strftime("%b %Y").upper() if appt_date else "")
        self.apptDoctor.setText(appt.clinic_name)
        self.apptNote.setText(f"{appt.purpose}")
        self.apptTime.setText(str(appt.appt_time))

    def _load_vaccine_progress(self):
        shots = self.vaccination_service.get_vaccinations_by_patient_id(self.patient_id)

        groups: dict[str, list] = {}
        for s in shots:
            key = s.vaccination_name.strip().lower()
            groups.setdefault(key, []).append(s)

        card_layout = self.cardVaccine.layout()
        if hasattr(self, "_vacc_container"):
            card_layout.removeWidget(self._vacc_container)
            self._vacc_container.deleteLater()

        from PyQt6.QtWidgets import QWidget as _W
        container = _W()
        container.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        if not groups:
            empty = QLabel("No vaccinations logged yet.")
            empty.setStyleSheet("font-size: 12px; color: #8FA89F; background: transparent; padding: 16px 20px;")
            layout.addWidget(empty)
        else:
            entries = list(groups.values())[:3]
            for i, group_shots in enumerate(entries):
                name     = group_shots[0].vaccination_name
                total    = max(s.dose_number for s in group_shots)
                done     = sum(1 for s in group_shots if s.status == "Completed")
                complete = done >= total

                row = QHBoxLayout()
                row.setContentsMargins(20, 10, 20, 10)
                row.setSpacing(10)

                info = QVBoxLayout()
                info.setSpacing(2)
                lbl_name = QLabel(name)
                lbl_name.setStyleSheet("font-size: 12px; font-weight: bold; color: #1C2B25;")
                meta_text = f"{'Single dose' if total == 1 else f'{total}-dose series'}  ·  {'Complete' if complete else f'Dose {done} done'}"

                info.addWidget(lbl_name)
                meta_label = QLabel(meta_text)
                meta_label.setStyleSheet("font-size: 10px; color: #546860;")
                info.addWidget(meta_label)
                row.addLayout(info)

                row_widget = QWidget()
                row_widget.setStyleSheet("background: transparent;")
                row_widget.setLayout(row)
                layout.addWidget(row_widget)

                if i < len(entries) - 1:
                    div = QFrame()
                    div.setFrameShape(QFrame.Shape.HLine)
                    div.setStyleSheet("QFrame { color: #DDE8E3; margin: 0 20px; }")
                    layout.addWidget(div)

        for i in range(card_layout.count()):
            item = card_layout.itemAt(i)
            if item and item.spacerItem():
                card_layout.removeItem(item)
                break
        card_layout.addWidget(container)
        self._vacc_container = container


