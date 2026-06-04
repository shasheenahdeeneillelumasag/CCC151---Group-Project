from datetime import date, datetime

from PyQt6.QtWidgets import (
    QWidget, QFrame, QLabel, QHBoxLayout,
    QVBoxLayout, QMessageBox, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6 import uic

from services.vaccination_shot_service import VaccinationShotService
from services.document_service import DocumentService
from services.patient_service import PatientService
from core.app_settings import AppSettings
from models.vaccination_shot import VaccinationShot
from dialogs.dialog_add_vaccination import DialogAddVaccination


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


# Dose row inside a vaccine card 

def _build_dose_row(shot: VaccinationShot, show_divider: bool) -> QFrame:
    row = QFrame()
    if show_divider:
        row.setStyleSheet("QFrame { border-bottom: 1px solid #DDE8E3; }")

    layout = QHBoxLayout(row)
    layout.setContentsMargins(14, 10, 14, 10)
    layout.setSpacing(10)

    label = QLabel(f"Dose {shot.dose_number}")
    label.setStyleSheet("font-size: 12px; color: #546860; font-weight: 500;")
    layout.addWidget(label)

    layout.addStretch()

    date_lbl = QLabel(_fmt_date(shot.date_administered))
    date_lbl.setStyleSheet("font-size: 12px; font-weight: bold; color: #1C2B25;")
    layout.addWidget(date_lbl)

    status = shot.status
    if status == "Completed":
        bg, fg, text = "#E3F5EE", "#0D6B52", "Administered"
    elif status == "Pending":
        bg, fg, text = "#FEF3DC", "#7A4D0A", "Scheduled"
    else:
        bg, fg, text = "#FAE8E8", "#8A1F1F", "Missed"

    badge = QLabel(f"  {text}  ")
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
    layout.addWidget(badge)

    return row


# Scheduled next-dose row 

def _build_scheduled_row(schedule_date, dose_number: int, show_divider: bool) -> QFrame:
    row = QFrame()
    if show_divider:
        row.setStyleSheet("QFrame { border-bottom: 1px solid #DDE8E3; }")

    layout = QHBoxLayout(row)
    layout.setContentsMargins(14, 10, 14, 10)
    layout.setSpacing(10)

    label = QLabel(f"Dose {dose_number}  (scheduled)")
    label.setStyleSheet("font-size: 12px; color: #8FA89F; font-weight: 500;")
    layout.addWidget(label)

    layout.addStretch()

    date_lbl = QLabel(_fmt_date(schedule_date))
    date_lbl.setStyleSheet("font-size: 12px; font-weight: bold; color: #8FA89F;")
    layout.addWidget(date_lbl)

    badge = QLabel("  Scheduled  ")
    badge.setStyleSheet("""
        QLabel {
            background: #FEF3DC;
            color: #7A4D0A;
            font-size: 10px;
            font-weight: bold;
            border-radius: 20px;
            padding: 2px 4px;
        }
    """)
    badge.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
    layout.addWidget(badge)

    return row


#  Vaccine group card 

class VaccineCard(QFrame):

    def __init__(self,
                 vaccine_name: str,
                 facility: str,
                 shots: list[VaccinationShot],
                 documents: list,
                 on_add_dose,
                 on_delete):
        super().__init__()
        self.setObjectName("vaxCard")
        self.setStyleSheet("""
            QFrame#vaxCard {
                background: #FFFFFF;
                border: 1px solid #DDE8E3;
                border-radius: 14px;
            }
        """)

        shots_sorted = sorted(shots, key=lambda s: s.dose_number)
        administered = [s for s in shots_sorted if s.status == "Completed"]
        total_known  = max((s.dose_number for s in shots_sorted), default=1)

        all_complete = all(s.status == "Completed" for s in shots_sorted)
        has_pending  = any(s.status == "Pending" for s in shots_sorted)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(20, 18, 20, 18)
        outer.setSpacing(14)


        header = QHBoxLayout()
        header.setSpacing(14)

        icon = QLabel("💉")
        icon.setFixedSize(48, 48)
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet("QLabel { background: #E3F5EE; border-radius: 12px; font-size: 22px; }")
        header.addWidget(icon)

        title_col = QVBoxLayout()
        title_col.setSpacing(3)
        lbl_name = QLabel(vaccine_name)
        lbl_name.setStyleSheet("font-size: 15px; font-weight: bold; color: #1C2B25;")
        lbl_meta = QLabel(f"Facility: {facility}")
        lbl_meta.setStyleSheet("font-size: 12px; color: #546860;")
        title_col.addWidget(lbl_name)
        title_col.addWidget(lbl_meta)
        header.addLayout(title_col)
        header.addStretch()
        
        if all_complete:
            prog_bg, prog_fg, prog_text = "#E8F5EB", "#1F5C2E", "Complete"
        else:
            done = len(administered)
            prog_bg, prog_fg = "#FEF3DC", "#7A4D0A"
            prog_text = f"{done} of {total_known} done"

        prog_badge = QLabel(f"  {prog_text}  ")
        prog_badge.setStyleSheet(f"""
            QLabel {{
                background: {prog_bg};
                color: {prog_fg};
                font-size: 10px;
                font-weight: bold;
                border-radius: 20px;
                padding: 3px 11px;
            }}
        """)
        prog_badge.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        header.addWidget(prog_badge)

        if not all_complete or has_pending:
            add_btn_lbl = QLabel("+ Add Dose")
            add_btn_lbl.setCursor(Qt.CursorShape.PointingHandCursor)
            add_btn_lbl.setStyleSheet("""
                QLabel {
                    background: transparent;
                    color: #546860;
                    font-size: 11px;
                    font-weight: 600;
                    border: 1px solid #C8D9D2;
                    border-radius: 8px;
                    padding: 6px 14px;
                }
                QLabel:hover { background: #E3F5EE; }
            """)
            add_btn_lbl.mousePressEvent = lambda e: on_add_dose()
            header.addWidget(add_btn_lbl)

        del_lbl = QLabel("🗑")
        del_lbl.setCursor(Qt.CursorShape.PointingHandCursor)
        del_lbl.setStyleSheet("font-size: 14px; color: #C0C0C0;")
        del_lbl.setToolTip("Delete all doses of this vaccine")
        del_lbl.mousePressEvent = lambda e: on_delete(shots)
        header.addWidget(del_lbl)

        outer.addLayout(header)

        pips = QHBoxLayout()
        pips.setSpacing(4)
        for i in range(total_known):
            pip = QFrame()
            pip.setFixedSize(28, 8)
            done = i < len(administered)
            pip.setStyleSheet(
                f"QFrame {{ background: {'#1A9E78' if done else '#C8D9D2'}; border-radius: 4px; }}"
            )
            pips.addWidget(pip)
        pips.addStretch()
        outer.addLayout(pips)

        #  Dose schedule table 
        schedule_frame = QFrame()
        schedule_frame.setObjectName("scheduleFrame")
        header_color = "#E8F5EB" if all_complete else "#E3F5EE"
        header_fg    = "#1F5C2E" if all_complete else "#0D6B52"
        header_text  = "DOSE SCHEDULE" if all_complete else "DOSE SCHEDULE — AUTO-CALCULATED"
        schedule_frame.setStyleSheet("""
            QFrame#scheduleFrame {
                background: #F8FBFA;
                border: 1px solid #DDE8E3;
                border-radius: 9px;
            }
        """)
        sf_layout = QVBoxLayout(schedule_frame)
        sf_layout.setContentsMargins(0, 0, 0, 0)
        sf_layout.setSpacing(0)

        sf_header = QLabel(f"  {header_text}")
        sf_header.setStyleSheet(f"""
            QLabel {{
                background: {header_color};
                color: {header_fg};
                font-size: 10px;
                font-weight: bold;
                letter-spacing: 0.5px;
                padding: 10px 14px;
                border-top-left-radius: 9px;
                border-top-right-radius: 9px;
            }}
        """)
        sf_layout.addWidget(sf_header)

        for i, shot in enumerate(shots_sorted):
            show_div = (i < len(shots_sorted) - 1) or shot.schedule_date
            row_widget = _build_dose_row(shot, show_divider=True)
            sf_layout.addWidget(row_widget)


            if shot.schedule_date and shot.status == "Pending":
                pass 

        latest = shots_sorted[-1] if shots_sorted else None
        if latest and latest.status == "Completed" and latest.schedule_date:
            next_dose_num = latest.dose_number + 1
            sched_row = _build_scheduled_row(latest.schedule_date, next_dose_num, show_divider=True)
            sf_layout.addWidget(sched_row)

        outer.addWidget(schedule_frame)

        if documents:
            docs_row = QHBoxLayout()
            docs_row.setSpacing(6)
            for doc in documents:
                doc_lbl = QLabel(f"📎  {doc.doc_filename}")
                doc_lbl.setStyleSheet("""
                    QLabel {
                        background: #F1EFE8;
                        border: 1px solid #DDE8E3;
                        border-radius: 20px;
                        font-size: 10px;
                        color: #546860;
                        padding: 3px 10px;
                    }
                """)
                doc_lbl.setMaximumWidth(220)
                docs_row.addWidget(doc_lbl)
            docs_row.addStretch()
            outer.addLayout(docs_row)

#  Main page 

class PageVaccinations(QWidget):

    def __init__(self):
        super().__init__()
        uic.loadUi("ui/page_vaccinations.ui", self)

        self.vaccination_service = VaccinationShotService()
        self.document_service    = DocumentService()
        self.patient_service     = PatientService()
        self.settings            = AppSettings()

        self.active_patient = self.patient_service.get_patient_by_code(
            self.settings.get_active_patient_code()
        )
        self.patient_id = self.active_patient.patient_id

        self.btnLogVax.clicked.connect(self._open_add_dialog)

        self.load_vaccinations()

    # Load 

    def load_vaccinations(self):
        shots = self.vaccination_service.get_vaccinations_by_patient_id(
            self.patient_id
        )
        groups: dict[str, list[VaccinationShot]] = {}
        for shot in shots:
            key = shot.vaccination_name.strip().lower()
            groups.setdefault(key, []).append(shot)

        self._populate(groups)

    def _populate(self, groups: dict[str, list[VaccinationShot]]):
        if hasattr(self, "_cards_container"):
            self._cards_container.deleteLater()

        from PyQt6.QtWidgets import QWidget as _W
        container = _W()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        if not groups:
            empty = QLabel("No vaccinations logged yet.")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setStyleSheet("font-size: 13px; color: #8FA89F; padding: 40px 0;")
            layout.addWidget(empty)
        else:
            for name_key, shots in groups.items():
                vaccine_name = shots[0].vaccination_name
                facility     = shots[0].facility

                docs = []
                seen_docs = set()
                for shot in shots:
                    for doc in self.document_service.get_documents_by_vaccine_id(shot.vaccine_id):
                        if doc.doc_id not in seen_docs:
                            seen_docs.add(doc.doc_id)
                            docs.append(doc)

                card = VaccineCard(
                    vaccine_name=vaccine_name,
                    facility=facility,
                    shots=shots,
                    documents=docs,
                    on_add_dose=self._open_add_dialog,
                    on_delete=self._delete_shots
                )
                layout.addWidget(card)

        scroll_layout = self.scrollContent.layout()
        scroll_layout.insertWidget(0, container)
        self._cards_container = container

    #  Dialog

    def _open_add_dialog(self):
        dialog = DialogAddVaccination(self.patient_id)
        if dialog.exec():
            self.load_vaccinations()

    #  Delete 

    def _delete_shots(self, shots: list[VaccinationShot]):
        name = shots[0].vaccination_name if shots else "this vaccination"
        reply = QMessageBox.question(
            self,
            "Delete Vaccination",
            f"Delete all doses of '{name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        for shot in shots:
            self.vaccination_service.delete_vaccination(shot.vaccine_id)

        self.load_vaccinations()
