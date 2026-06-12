import os
import shutil

DOCS_DIR = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "documents")
)
from datetime import date

from PyQt6.QtCore import Qt, QDate
from PyQt6.QtWidgets import (
    QDialog, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QFrame, QMessageBox,
    QFileDialog,
)
from PyQt6 import uic

from services.container import *
from widgets.date_picker import init_date_picker, set_date_picker, get_date_from_picker, get_date_str_from_picker

_ROW_STYLE = (
    "QFrame { background: #FFFFFF; border: 1px solid #DDE8E3; "
    "border-radius: 8px; }"
)
_LABEL_STYLE = "QLabel { font-size: 12px; color: #1C2B25; }"
_SUB_STYLE   = "QLabel { font-size: 10px; color: #8FA89E; }"
_DEL_STYLE   = (
    "QPushButton { background: transparent; color: #C0392B; "
    "border: 1px solid #C0392B; border-radius: 6px; "
    "font-size: 11px; padding: 3px 8px; } "
    "QPushButton:hover { background: #FDECEB; }"
)


def _make_entry_row(primary: str, secondary: str) -> QFrame:
    """
    Returns a styled QFrame with:
      • primary text (bold, main line)
      • secondary text (muted, sub-line)
      • a Delete button on the right

    The Delete button emits clicked; callers connect to it to remove the row.
    """
    frame = QFrame()
    frame.setStyleSheet(_ROW_STYLE)

    outer = QHBoxLayout(frame)
    outer.setContentsMargins(12, 8, 10, 8)
    outer.setSpacing(8)

    text_block = QVBoxLayout()
    text_block.setSpacing(2)

    lbl_primary = QLabel(primary)
    lbl_primary.setStyleSheet(_LABEL_STYLE)
    lbl_primary.setWordWrap(True)

    lbl_secondary = QLabel(secondary)
    lbl_secondary.setStyleSheet(_SUB_STYLE)
    lbl_secondary.setWordWrap(True)

    text_block.addWidget(lbl_primary)
    if secondary:
        text_block.addWidget(lbl_secondary)

    outer.addLayout(text_block, stretch=1)

    btn_del = QPushButton("Delete")
    btn_del.setStyleSheet(_DEL_STYLE)
    btn_del.setFixedHeight(28)
    btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
    outer.addWidget(btn_del, alignment=Qt.AlignmentFlag.AlignVCenter)

    frame.btn_delete = btn_del 

    return frame

class DialogAddRecord(QDialog):

    def __init__(self, patient_id: int, parent=None):
        super().__init__(parent)

        uic.loadUi("ui/dialog_add_record.ui", self)
        self.setFixedSize(self.size())

        self.patient_id = patient_id

        self.visit_record_service = visit_record_service
        self.diagnosis_service     = diagnosis_service
        self.prescription_service  = prescription_service
        self.document_service      = document_service

        self._diagnoses:     list[dict] = []   
        self._prescriptions: list[dict] = []   
        self._files:         list[str]  = []  

        today = QDate.currentDate()
        init_date_picker(self.inputVisitDateMonth, self.inputVisitDateDay, self.inputVisitDateYear)
        init_date_picker(self.inputDiagnosisDateMonth, self.inputDiagnosisDateDay, self.inputDiagnosisDateYear)
        init_date_picker(self.inputRxDateMonth, self.inputRxDateDay, self.inputRxDateYear)
        set_date_picker(self.inputVisitDateMonth, self.inputVisitDateDay, self.inputVisitDateYear, today)
        set_date_picker(self.inputDiagnosisDateMonth, self.inputDiagnosisDateDay, self.inputDiagnosisDateYear, today)
        set_date_picker(self.inputRxDateMonth, self.inputRxDateDay, self.inputRxDateYear, today)



        self.btnCancel.clicked.connect(self._confirm_cancel)
        self.btnSave.clicked.connect(self._save)

        self.btnAddDiagnosis.clicked.connect(self._add_diagnosis)
        self.btnAddRx.clicked.connect(self._add_rx)
        self.uploadZone.mousePressEvent = lambda _e: self._pick_files()

    def _add_diagnosis(self):
        name = self.inputDiagnosisName.text().strip()
        if not name:
            QMessageBox.warning(self, "Missing Field", "Diagnosis name is required.")
            return

        desc = self.inputDiagnosisDescription.toPlainText().strip()
        d    = get_date_from_picker(self.inputDiagnosisDateMonth, self.inputDiagnosisDateDay, self.inputDiagnosisDateYear).toPyDate()

        entry = {"name": name, "description": desc, "date": d}
        self._diagnoses.append(entry)

        primary   = name
        secondary = f"{d.strftime('%B %d, %Y')}{'  ·  ' + desc if desc else ''}"
        row = _make_entry_row(primary, secondary)
        row.btn_delete.clicked.connect(
            lambda _checked, e=entry, r=row: self._remove_diagnosis(e, r)
        )
        self.diagnosisEntriesLayout.addWidget(row)

        self.inputDiagnosisName.clear()
        self.inputDiagnosisDescription.clear()
        set_date_picker(self.inputDiagnosisDateMonth, self.inputDiagnosisDateDay, self.inputDiagnosisDateYear, QDate.currentDate())

    def _remove_diagnosis(self, entry: dict, row: QFrame):
        self._diagnoses.remove(entry)
        row.deleteLater()

    def _add_rx(self):
        name         = self.inputRxName.text().strip()
        dosage       = self.inputRxDosage.text().strip()
        prescribed_by = self.inputRxPrescribedBy.text().strip()

        if not name or not dosage or not prescribed_by:
            QMessageBox.warning(
                self, "Missing Fields",
                "Medication name, dosage, and prescribing doctor are required."
            )
            return

        d = get_date_from_picker(self.inputRxDateMonth, self.inputRxDateDay, self.inputRxDateYear).toPyDate()

        entry = {
            "name": name, "dosage": dosage,
            "prescribed_by": prescribed_by, "date": d,
        }
        self._prescriptions.append(entry)

        primary   = f"{name}  —  {dosage}"
        secondary = f"{d.strftime('%B %d, %Y')}  ·  {prescribed_by}"
        row = _make_entry_row(primary, secondary)
        row.btn_delete.clicked.connect(
            lambda _checked, e=entry, r=row: self._remove_rx(e, r)
        )
        self.rxEntriesLayout.addWidget(row)
        self.inputRxName.clear()
        self.inputRxDosage.clear()
        self.inputRxPrescribedBy.clear()
        set_date_picker(self.inputRxDateMonth, self.inputRxDateDay, self.inputRxDateYear, QDate.currentDate())

    def _remove_rx(self, entry: dict, row: QFrame):
        self._prescriptions.remove(entry)
        row.deleteLater()

    def _pick_files(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select files to attach",
            "",
            "All files (*.*)",
        )
        for path in paths:
            if path and path not in self._files:
                self._files.append(path)
                self._add_file_row(path)

    def _add_file_row(self, path: str):
        filename  = os.path.basename(path)
        size_kb   = os.path.getsize(path) // 1024
        secondary = f"{size_kb} KB  ·  {path}"

        row = _make_entry_row(filename, secondary)
        row.btn_delete.clicked.connect(
            lambda _checked, p=path, r=row: self._remove_file(p, r)
        )
        self.uploadedFilesLayout.addWidget(row)

    def _remove_file(self, path: str, row: QFrame):
        if path in self._files:
            self._files.remove(path)
        row.deleteLater()

    def _save(self):
        visit_date = get_date_from_picker(self.inputVisitDateMonth, self.inputVisitDateDay, self.inputVisitDateYear).toPyDate()
        bp         = self.inputBP.text().strip() or None
        weight_raw = self.inputWeight.text().strip()

        weight_kg: float | None = None
        if weight_raw:
            try:
                weight_kg = float(weight_raw)
            except ValueError:
                QMessageBox.warning(self, "Invalid Weight", "Weight must be a number.")
                return

        record = self.visit_record_service.create_visit_record(
            patient_id  = self.patient_id,
            visit_date  = visit_date,
            weight_kg   = weight_kg,
            blood_pressure = bp,
        )
        record_id = record.record_id

        for d in self._diagnoses:
            self.diagnosis_service.create_diagnosis(
                record_id      = record_id,
                diagnosis_name = d["name"],
                description    = d["description"] or None,
                diagnosed_date = d["date"],
            )

        for rx in self._prescriptions:
            self.prescription_service.create_prescription(
                record_id       = record_id,
                medication_name = rx["name"],
                dosage          = rx["dosage"],
                prescribed_date = rx["date"],
                prescribed_by   = rx["prescribed_by"],
            )

        today = date.today()
        os.makedirs(DOCS_DIR, exist_ok=True)
        for filepath in self._files:
            filename = os.path.basename(filepath)
            dest = os.path.join(DOCS_DIR, filename)
            base, ext = os.path.splitext(filename)
            counter = 1
            while os.path.exists(dest):
                filename = f"{base}_{counter}{ext}"
                dest = os.path.join(DOCS_DIR, filename)
                counter += 1
            shutil.copy2(filepath, dest)
            self.document_service.create_record_document(
                doc_filename  = filename,
                date_uploaded = today,
                record_id     = record_id,
            )

        QMessageBox.information(self, "Success", "Health record saved successfully.")
        self.accept()

    def _confirm_cancel(self):
        reply = QMessageBox.question(
            self, "Discard Changes",
            "Are you sure you want to discard the changes?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.reject()
