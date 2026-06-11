import os
import shutil

DOCS_DIR = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "documents")
)
from datetime import date, datetime

from PyQt6.QtCore import Qt, QDate
from PyQt6.QtWidgets import (
    QDialog, QFrame, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QMessageBox, QFileDialog,
)
from PyQt6 import uic

from services.visit_record_service import VisitRecordService
from services.diagnosis_service import DiagnosisService
from services.prescription_service import PrescriptionService
from services.document_service import DocumentService
from widgets.date_picker import init_date_picker, set_date_picker, get_date_from_picker


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


def _parse_date(value):
    """Accept a date object, datetime, or YYYY-MM-DD string."""
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        return datetime.strptime(value[:10], "%Y-%m-%d").date()
    raise ValueError(f"Cannot parse date: {value!r}")


class DialogEditRecord(QDialog):

    def __init__(self, history_item, parent=None):
        super().__init__(parent)

        uic.loadUi("ui/dialog_add_record.ui", self)
        self.setFixedSize(self.size())

        self.setWindowTitle("Edit Health Record")
        self.label.setText("Edit Health Record")
        self.btnSave.setText("Save Changes")

        self.history_item = history_item
        self.record       = history_item.record

        self.visit_record_service = VisitRecordService()
        self.diagnosis_service    = DiagnosisService()
        self.prescription_service = PrescriptionService()
        self.document_service     = DocumentService()

    
        self._diagnoses:     list[dict] = []
        self._prescriptions: list[dict] = []
        self._files:         list[str]  = []  

        today = QDate.currentDate()
        init_date_picker(self.inputVisitDateMonth, self.inputVisitDateDay, self.inputVisitDateYear)
        init_date_picker(self.inputDiagnosisDateMonth, self.inputDiagnosisDateDay, self.inputDiagnosisDateYear)
        init_date_picker(self.inputRxDateMonth, self.inputRxDateDay, self.inputRxDateYear)
        set_date_picker(self.inputDiagnosisDateMonth, self.inputDiagnosisDateDay, self.inputDiagnosisDateYear, today)
        set_date_picker(self.inputRxDateMonth, self.inputRxDateDay, self.inputRxDateYear, today)

        self._prefill()

        # Wire buttons
        self.btnClose.clicked.connect(self._confirm_cancel)
        self.btnCancel.clicked.connect(self._confirm_cancel)
        self.btnSave.clicked.connect(self._save)
        self.btnAddDiagnosis.clicked.connect(self._add_diagnosis)
        self.btnAddRx.clicked.connect(self._add_rx)
        self.uploadZone.mousePressEvent = lambda _e: self._pick_files()

    def _prefill(self):
        r = self.record

        # Visit date — may be a string "YYYY-MM-DD" from SQLite
        vd = _parse_date(r.visit_date)
        set_date_picker(self.inputVisitDateMonth, self.inputVisitDateDay, self.inputVisitDateYear, QDate(vd.year, vd.month, vd.day))

        # Vitals
        self.inputBP.setText(r.blood_pressure or "")
        self.inputWeight.setText(
            str(r.weight_kg) if r.weight_kg is not None else ""
        )

        # Default sub-form dates to today
        today = QDate.currentDate()
        set_date_picker(self.inputDiagnosisDateMonth, self.inputDiagnosisDateDay, self.inputDiagnosisDateYear, today)
        set_date_picker(self.inputRxDateMonth, self.inputRxDateDay, self.inputRxDateYear, today)

        for d in self.history_item.diagnoses:
            entry = {
                "id": d.diagnosis_id,
                "name": d.diagnosis_name,
                "description": d.description or "",
                "date": _parse_date(d.diagnosed_date),
                "_delete": False,
            }
            self._diagnoses.append(entry)
            self._render_diagnosis_row(entry)

        for p in self.history_item.prescriptions:
            entry = {
                "id": p.prescription_id,
                "name": p.medication_name,
                "dosage": p.dosage,
                "prescribed_by": p.prescribed_by,
                "date": _parse_date(p.prescribed_date),
                "_delete": False,
            }
            self._prescriptions.append(entry)
            self._render_rx_row(entry)

    def _add_diagnosis(self):
        name = self.inputDiagnosisName.text().strip()
        if not name:
            QMessageBox.warning(self, "Missing Field", "Diagnosis name is required.")
            return

        desc = self.inputDiagnosisDescription.toPlainText().strip()
        d    = get_date_from_picker(self.inputDiagnosisDateMonth, self.inputDiagnosisDateDay, self.inputDiagnosisDateYear).toPyDate()

        entry = {"id": None, "name": name, "description": desc, "date": d, "_delete": False}
        self._diagnoses.append(entry)
        self._render_diagnosis_row(entry)

        self.inputDiagnosisName.clear()
        self.inputDiagnosisDescription.clear()
        set_date_picker(self.inputDiagnosisDateMonth, self.inputDiagnosisDateDay, self.inputDiagnosisDateYear, QDate.currentDate())

    def _render_diagnosis_row(self, entry: dict):
        d         = entry["date"]
        date_str  = d.strftime("%B %d, %Y")
        desc      = entry.get("description", "")
        secondary = f"{date_str}{'  ·  ' + desc if desc else ''}"

        row = _make_entry_row(entry["name"], secondary)
        row.btn_delete.clicked.connect(
            lambda _checked, e=entry, r=row: self._remove_diagnosis(e, r)
        )
        self.diagnosisEntriesLayout.addWidget(row)

    def _remove_diagnosis(self, entry: dict, row: QFrame):
        entry["_delete"] = True
        row.deleteLater()

    def _add_rx(self):
        name          = self.inputRxName.text().strip()
        dosage        = self.inputRxDosage.text().strip()
        prescribed_by = self.inputRxPrescribedBy.text().strip()

        if not name or not dosage or not prescribed_by:
            QMessageBox.warning(
                self, "Missing Fields",
                "Medication name, dosage, and prescribing doctor are required."
            )
            return

        d = get_date_from_picker(self.inputRxDateMonth, self.inputRxDateDay, self.inputRxDateYear).toPyDate()
        entry = {
            "id": None, "name": name, "dosage": dosage,
            "prescribed_by": prescribed_by, "date": d, "_delete": False,
        }
        self._prescriptions.append(entry)
        self._render_rx_row(entry)

        self.inputRxName.clear()
        self.inputRxDosage.clear()
        self.inputRxPrescribedBy.clear()
        set_date_picker(self.inputRxDateMonth, self.inputRxDateDay, self.inputRxDateYear, QDate.currentDate())

    def _render_rx_row(self, entry: dict):
        d         = entry["date"]
        date_str  = d.strftime("%B %d, %Y")
        primary   = f"{entry['name']}  —  {entry['dosage']}"
        secondary = f"{date_str}  ·  {entry['prescribed_by']}"

        row = _make_entry_row(primary, secondary)
        row.btn_delete.clicked.connect(
            lambda _checked, e=entry, r=row: self._remove_rx(e, r)
        )
        self.rxEntriesLayout.addWidget(row)

    def _remove_rx(self, entry: dict, row: QFrame):
        entry["_delete"] = True
        row.deleteLater()

    def _pick_files(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Select files to attach", "", "All files (*.*)",
        )
        for path in paths:
            if path and path not in self._files:
                self._files.append(path)
                self._add_file_row(path)

    def _add_file_row(self, path: str):
        filename  = os.path.basename(path)
        size_kb   = os.path.getsize(path) // 1024
        row = _make_entry_row(filename, f"{size_kb} KB  ·  {path}")
        row.btn_delete.clicked.connect(
            lambda _checked, p=path, r=row: self._remove_file(p, r)
        )
        self.uploadedFilesLayout.addWidget(row)

    def _remove_file(self, path: str, row: QFrame):
        if path in self._files:
            self._files.remove(path)
        row.deleteLater()

    def _save(self):
        try:
            self._do_save()
        except Exception as exc:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(
                self, "Save Failed",
                f"An error occurred while saving:\n\n{exc}"
            )

    def _do_save(self):
        visit_date = get_date_from_picker(self.inputVisitDateMonth, self.inputVisitDateDay, self.inputVisitDateYear).toPyDate()
        bp         = self.inputBP.text().strip() or None
        weight_raw = self.inputWeight.text().strip()

        weight_kg = None
        if weight_raw:
            try:
                weight_kg = float(weight_raw)
            except ValueError:
                QMessageBox.warning(self, "Invalid Weight", "Weight must be a number.")
                return

        self.visit_record_service.update_visit_record(
            record_id      = self.record.record_id,
            patient_id     = self.record.patient_id,
            visit_date     = visit_date,
            weight_kg      = weight_kg,
            blood_pressure = bp,
        )

        record_id = self.record.record_id

        for d in self._diagnoses:
            if d["_delete"] and d["id"]:
                self.diagnosis_service.delete_diagnosis(d["id"])
            elif not d["_delete"] and d["id"] is None:
                self.diagnosis_service.create_diagnosis(
                    record_id      = record_id,
                    diagnosis_name = d["name"],
                    description    = d["description"] or None,
                    diagnosed_date = d["date"],
                )

        for rx in self._prescriptions:
            if rx["_delete"] and rx["id"]:
                self.prescription_service.delete_prescription(rx["id"])
            elif not rx["_delete"] and rx["id"] is None:
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

        QMessageBox.information(self, "Success", "Health record updated successfully.")
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