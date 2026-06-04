import os
import shutil
from datetime import date

from PyQt6.QtWidgets import (
    QWidget, QFrame, QLabel, QGridLayout,
    QVBoxLayout, QHBoxLayout, QMessageBox,
    QFileDialog, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
from PyQt6 import uic

from services.document_service import DocumentService
from services.visit_record_service import VisitRecordService
from services.vaccination_shot_service import VaccinationShotService
from services.diagnosis_service import DiagnosisService
from services.prescription_service import PrescriptionService
from services.patient_service import PatientService
from core.app_settings import AppSettings
from models.document import Document

DOCS_DIR = "documents"


def _preview_style(filename: str) -> tuple[str, str]:
    """Return (bg_color, border_color) for the preview thumbnail."""
    ext = os.path.splitext(filename)[1].lower()
    if ext in (".jpg", ".jpeg", ".png", ".gif", ".webp"):
        return "#F8FBFA", "#DDE8E3"
    elif ext == ".pdf":
        return "#EEEAFC", "#AFA9EC"
    else:
        return "#FEF3DC", "#FAC775"


def _preview_icon(filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    if ext in (".jpg", ".jpeg", ".png", ".gif", ".webp"):
        return "🖼"
    elif ext == ".pdf":
        return "📄"
    else:
        return "📎"


def _badge_style(link_type: str) -> tuple[str, str, str]:
    """Return (label, bg, color) badge for the document type."""
    styles = {
        "vaccine":      ("Vaccination", "#E3F5EE", "#0D6B52"),
        "record":       ("Visit",       "#EAF3FC", "#1A4F8A"),
        "diagnosis":    ("Diagnosis",   "#EEEAFC", "#3D2F88"),
        "prescription": ("Prescription","#FEF3DC", "#7A4D0A"),
    }
    return styles.get(link_type, ("Document", "#F0F0F0", "#555555"))


def _resolve_link(doc: Document,
                  visit_service: VisitRecordService,
                  vaccine_service: VaccinationShotService,
                  diagnosis_service: DiagnosisService,
                  prescription_service: PrescriptionService
                  ) -> tuple[str, str]:
    """Return (link_text, link_type) describing what this document is linked to."""
    if doc.vaccine_id is not None:
        v = vaccine_service.get_vaccination_by_id(doc.vaccine_id)
        text = f"{v.vaccination_name} — Dose {v.dose_number}" if v else f"Vaccine #{doc.vaccine_id}"
        return text, "vaccine"
    if doc.record_id is not None:
        r = visit_service.get_visit_record_by_id(doc.record_id)
        text = f"Visit {r.record_code} — {r.visit_date}" if r else f"Visit #{doc.record_id}"
        return text, "record"
    if doc.diagnosis_id is not None:
        d = diagnosis_service.get_diagnosis_by_id(doc.diagnosis_id)
        text = d.diagnosis_name if d else f"Diagnosis #{doc.diagnosis_id}"
        return text, "diagnosis"
    if doc.prescription_id is not None:
        p = prescription_service.get_prescription_by_id(doc.prescription_id)
        text = p.medication_name if p else f"Prescription #{doc.prescription_id}"
        return text, "prescription"
    return "Unlinked", "record"


# Document card widget 

class DocCard(QFrame):
    clicked = pyqtSignal(object) 
    delete_requested = pyqtSignal(object)

    def __init__(self, doc: Document, link_text: str, link_type: str):
        super().__init__()
        self.doc = doc
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        bg, border = _preview_style(doc.doc_filename)
        icon = _preview_icon(doc.doc_filename)
        badge_label, badge_bg, badge_fg = _badge_style(link_type)

        date_str = doc.date_uploaded
        if isinstance(date_str, date):
            date_str = date_str.strftime("%b %d, %Y")

        self.setObjectName("docCard")
        self.setStyleSheet("""
            QFrame#docCard {
                background: #FFFFFF;
                border: 1px solid #DDE8E3;
                border-radius: 14px;
            }
            QFrame#docCard:hover {
                border-color: #9FE1CB;
                background: #F8FBFA;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        preview = QFrame()
        preview.setMinimumHeight(80)
        preview.setMaximumHeight(80)
        preview.setStyleSheet(f"""
            QFrame {{
                background: {bg};
                border: 1px solid {border};
                border-radius: 9px;
            }}
        """)
        prev_layout = QVBoxLayout(preview)
        prev_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        full_path = os.path.join(DOCS_DIR, doc.doc_filename)
        ext = os.path.splitext(doc.doc_filename)[1].lower()
        if ext in (".jpg", ".jpeg", ".png", ".webp") and os.path.exists(full_path):
            pix = QPixmap(full_path).scaled(
                160, 72,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            thumb = QLabel()
            thumb.setPixmap(pix)
            thumb.setAlignment(Qt.AlignmentFlag.AlignCenter)
            prev_layout.addWidget(thumb)
        else:
            icon_lbl = QLabel(icon)
            icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon_lbl.setStyleSheet("font-size: 28px;")
            prev_layout.addWidget(icon_lbl)

        layout.addWidget(preview)

        name_lbl = QLabel(doc.doc_filename)
        name_lbl.setStyleSheet("font-size: 12px; font-weight: bold; color: #1C2B25;")
        name_lbl.setWordWrap(True)
        layout.addWidget(name_lbl)

        link_lbl = QLabel(f"Linked: {link_text}")
        link_lbl.setStyleSheet("font-size: 10px; color: #546860;")
        link_lbl.setWordWrap(True)
        layout.addWidget(link_lbl)

        date_lbl = QLabel(date_str)
        date_lbl.setStyleSheet("font-size: 10px; color: #8FA89F;")
        layout.addWidget(date_lbl)

        bottom = QHBoxLayout()
        bottom.setContentsMargins(0, 0, 0, 0)

        badge = QLabel(f"  {badge_label}  ")
        badge.setStyleSheet(f"""
            QLabel {{
                background: {badge_bg};
                color: {badge_fg};
                font-size: 9px;
                font-weight: bold;
                border-radius: 20px;
                padding: 2px 4px;
            }}
        """)
        badge.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        bottom.addWidget(badge)
        bottom.addStretch()

        del_btn = QLabel("🗑")
        del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        del_btn.setStyleSheet("font-size: 14px; color: #C0C0C0;")
        del_btn.setToolTip("Delete document")
        del_btn.mousePressEvent = lambda e, d=doc: self.delete_requested.emit(d)
        bottom.addWidget(del_btn)

        layout.addLayout(bottom)

    def mousePressEvent(self, event):
        self.clicked.emit(self.doc)
        super().mousePressEvent(event)


# Main page 

class PageDocuments(QWidget):

    TAB_ALL          = 0
    TAB_VACCINATIONS = 1
    TAB_VISITS       = 2
    TAB_DIAGNOSES    = 3
    TAB_PRESCRIPTIONS= 4

    def __init__(self):
        super().__init__()
        uic.loadUi("ui/page_documents.ui", self)

        self.doc_service          = DocumentService()
        self.visit_service        = VisitRecordService()
        self.vaccine_service      = VaccinationShotService()
        self.diagnosis_service    = DiagnosisService()
        self.prescription_service = PrescriptionService()
        self.patient_service      = PatientService()
        self.settings             = AppSettings()

        self.active_patient = self.patient_service.get_patient_by_code(
            self.settings.get_active_patient_code()
        )
        self.patient_id = self.active_patient.patient_id

        os.makedirs(DOCS_DIR, exist_ok=True)

        self._setup_tabs()
        self._current_tab = self.TAB_ALL

        self.btnUpload.clicked.connect(self._upload_document)
        self.tabBar.currentChanged.connect(self._on_tab_changed)
        self.uploadZone.mousePressEvent = lambda e: self._upload_document()

        self.load_documents()

    #  Tab setup

    def _setup_tabs(self):
        for label in ("All", "Vaccinations", "Visits", "Diagnoses", "Prescriptions"):
            self.tabBar.addTab(label)

    def _on_tab_changed(self, index: int):
        self._current_tab = index
        self.load_documents()

    #  Load & populate 

    def _get_patient_docs(self) -> list[Document]:
        """Fetch all documents that belong to the active patient."""
        patient_docs = []

        from services.visit_record_service import VisitRecordService
        records = self.visit_service.get_visit_records_by_patient_id(self.patient_id)
        record_ids = {r.record_id for r in records}

        diagnosis_ids = set()
        for r in records:
            for d in self.diagnosis_service.get_diagnoses_by_record_id(r.record_id):
                diagnosis_ids.add(d.diagnosis_id)

        prescription_ids = set()
        for r in records:
            for p in self.prescription_service.get_prescriptions_by_record_id(r.record_id):
                prescription_ids.add(p.prescription_id)

        vaccines = self.vaccine_service.get_vaccinations_by_patient_id(self.patient_id)
        vaccine_ids = {v.vaccine_id for v in vaccines}

        seen = set()
        def _add(docs):
            for d in docs:
                if d.doc_id not in seen:
                    seen.add(d.doc_id)
                    patient_docs.append(d)

        for rid in record_ids:
            _add(self.doc_service.get_documents_by_record_id(rid))
        for did in diagnosis_ids:
            _add(self.doc_service.get_documents_by_diagnosis_id(did))
        for pid in prescription_ids:
            _add(self.doc_service.get_documents_by_prescription_id(pid))
        for vid in vaccine_ids:
            _add(self.doc_service.get_documents_by_vaccine_id(vid))

        patient_docs.sort(
            key=lambda d: d.date_uploaded if d.date_uploaded else "",
            reverse=True
        )
        return patient_docs

    def _filter_docs(self, docs: list[Document]) -> list[Document]:
        tab = self._current_tab
        if tab == self.TAB_ALL:
            return docs
        elif tab == self.TAB_VACCINATIONS:
            return [d for d in docs if d.vaccine_id is not None]
        elif tab == self.TAB_VISITS:
            return [d for d in docs if d.record_id is not None]
        elif tab == self.TAB_DIAGNOSES:
            return [d for d in docs if d.diagnosis_id is not None]
        elif tab == self.TAB_PRESCRIPTIONS:
            return [d for d in docs if d.prescription_id is not None]
        return docs

    def load_documents(self):
        all_docs = self._get_patient_docs()
        docs = self._filter_docs(all_docs)
        self._populate_grid(docs)
        self._update_tab_counts(all_docs)

    def _update_tab_counts(self, all_docs: list[Document]):
        counts = [
            len(all_docs),
            sum(1 for d in all_docs if d.vaccine_id is not None),
            sum(1 for d in all_docs if d.record_id is not None),
            sum(1 for d in all_docs if d.diagnosis_id is not None),
            sum(1 for d in all_docs if d.prescription_id is not None),
        ]
        labels = ["All", "Vaccinations", "Visits", "Diagnoses", "Prescriptions"]
        for i, (label, count) in enumerate(zip(labels, counts)):
            self.tabBar.setTabText(i, f"{label} ({count})")

    def _populate_grid(self, docs: list[Document]):
        grid: QGridLayout = self.scrollContent.findChild(QGridLayout, "docGrid")
        if grid is None:
            layout = self.scrollContent.layout()
            for i in range(layout.count()):
                item = layout.itemAt(i)
                if item and isinstance(item.layout(), QGridLayout):
                    grid = item.layout()
                    break

        if grid:
            while grid.count():
                item = grid.takeAt(0)
                w = item.widget()
                if w:
                    w.deleteLater()

        if not docs:
            empty = QLabel("No documents found.")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setStyleSheet("font-size: 13px; color: #8FA89F; padding: 40px;")
            if grid:
                grid.addWidget(empty, 0, 0, 1, 2)
            return

        col_count = 2
        for idx, doc in enumerate(docs):
            link_text, link_type = _resolve_link(
                doc,
                self.visit_service,
                self.vaccine_service,
                self.diagnosis_service,
                self.prescription_service
            )
            card = DocCard(doc, link_text, link_type)
            card.clicked.connect(self._open_document)
            card.delete_requested.connect(self._delete_document)
            row, col = divmod(idx, col_count)
            if grid:
                grid.addWidget(card, row, col)

    #  Upload 

    def _upload_document(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Upload Document",
            "",
            "Images & PDFs (*.jpg *.jpeg *.png *.pdf);;All Files (*)"
        )

        if not path:
            return

        filename = os.path.basename(path)
        dest = os.path.join(DOCS_DIR, filename)

        base, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(dest):
            filename = f"{base}_{counter}{ext}"
            dest = os.path.join(DOCS_DIR, filename)
            counter += 1

        shutil.copy2(path, dest)

        records = self.visit_service.get_visit_records_by_patient_id(self.patient_id)
        record_id = records[0].record_id if records else None

        self.doc_service.create_record_document(
            doc_filename=filename,
            date_uploaded=date.today(),
            record_id=record_id
        ) if record_id else self.doc_service._create_document(
            doc_filename=filename,
            date_uploaded=date.today()
        )

        self.load_documents()

    #  Open 

    def _open_document(self, doc: Document):
        full_path = os.path.join(DOCS_DIR, doc.doc_filename)

        if not os.path.exists(full_path):
            QMessageBox.warning(
                self,
                "File Not Found",
                f"The file '{doc.doc_filename}' could not be found on disk.\n\n"
                f"Expected path: {os.path.abspath(full_path)}"
            )
            return

        import subprocess, sys
        if sys.platform == "win32":
            os.startfile(full_path)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", full_path])
        else:
            subprocess.Popen(["xdg-open", full_path])

    #  Delete 

    def _delete_document(self, doc: Document):
        reply = QMessageBox.question(
            self,
            "Delete Document",
            f"Delete '{doc.doc_filename}'?\n\nThe file will be removed from disk.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # Remove from disk
        full_path = os.path.join(DOCS_DIR, doc.doc_filename)
        if os.path.exists(full_path):
            os.remove(full_path)

        # Remove from DB
        self.doc_service.delete_document(doc.doc_id)

        self.load_documents()
