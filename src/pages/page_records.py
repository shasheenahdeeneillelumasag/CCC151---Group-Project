from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QFrame,
    QHBoxLayout,
    QVBoxLayout,
    QMessageBox
)

from PyQt6 import uic
from PyQt6.QtCore import Qt

from services.visit_record_service import VisitRecordService


class PageRecords(QWidget):

    def __init__(self, patient_id: int):
        super().__init__()

        uic.loadUi("ui/page_records.ui", self)

        self.patient_id = patient_id
        self.service = VisitRecordService()

        self.setup_tabs()
        self.load_records()

        self.searchInput.textChanged.connect(self.on_search)
        self.tabBar.currentChanged.connect(self.on_tab_changed)
        self.btnNewRecord.clicked.connect(self.on_new_record)

    # =========================================================
    # UI SETUP
    # =========================================================

    def setup_tabs(self):

        self.tabBar.addTab("All")
        self.tabBar.addTab("Checkup")
        self.tabBar.addTab("Annual PE")
        self.tabBar.addTab("ER Visit")

    # =========================================================
    # LOAD RECORDS
    # =========================================================

    def load_records(self, keyword: str = "", category: str = "All"):

        # remove old widgets
        self.clear_record_widgets()

        # fetch records
        records = self.service.get_visit_records_by_patient_id(
            self.patient_id
        )

        # search filter
        if keyword:
            keyword = keyword.lower()

            records = [
                r for r in records
                if keyword in (r.record_code or "").lower()
            ]

        # category filter
        if category != "All":
            records = [
                r for r in records
                if getattr(r, "category", "") == category
            ]

        # render
        for record in records:
            card = self.create_record_card(record)
            self.recordsContainer.layout().addWidget(card)

        self.recordsContainer.layout().addStretch()

    # =========================================================
    # RECORD CARD
    # =========================================================

    def create_record_card(self, record):

        frame = QFrame()
        frame.setObjectName("recordCard")

        layout = QHBoxLayout(frame)
        layout.setContentsMargins(20, 14, 20, 14)

        # icon
        icon = QLabel("📋")
        icon.setFixedSize(42, 42)
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon.setStyleSheet("""
            background: #EAF3FC;
            border-radius: 10px;
            font-size: 18px;
        """)

        layout.addWidget(icon)

        # content
        content_layout = QVBoxLayout()

        title = QLabel(
            f"{record.visit_date} — {record.record_code}"
        )

        title.setStyleSheet("""
            font-size: 13px;
            font-weight: bold;
            color: #1C2B25;
        """)

        content_layout.addWidget(title)

        vitals = QLabel(
            f"BP: {record.blood_pressure or '-'}  ·  "
            f"Weight: {record.weight_kg or '-'} kg"
        )

        vitals.setStyleSheet("""
            font-size: 11px;
            color: #546860;
        """)

        content_layout.addWidget(vitals)

        patient = QLabel(
            f"Patient ID: {record.patient_id}"
        )

        patient.setStyleSheet("""
            font-size: 10px;
            color: #8FA89F;
        """)

        content_layout.addWidget(patient)

        layout.addLayout(content_layout)

        layout.addStretch()

        # tag
        tag = QLabel(
            getattr(record, "category", "Record")
        )

        tag.setStyleSheet("""
            background: #EAF3FC;
            color: #1A4F8A;
            font-size: 10px;
            font-weight: bold;
            border-radius: 20px;
            padding: 4px 10px;
        """)

        layout.addWidget(tag)

        return frame

    # =========================================================
    # HELPERS
    # =========================================================

    def clear_record_widgets(self):

        layout = self.recordsContainer.layout()

        while layout.count():

            item = layout.takeAt(0)

            widget = item.widget()

            if widget:
                widget.deleteLater()

    # =========================================================
    # EVENTS
    # =========================================================

    def on_search(self):

        keyword = self.searchInput.text()

        category = self.tabBar.tabText(
            self.tabBar.currentIndex()
        )

        self.load_records(keyword, category)

    def on_tab_changed(self):

        keyword = self.searchInput.text()

        category = self.tabBar.tabText(
            self.tabBar.currentIndex()
        )

        self.load_records(keyword, category)

    def on_new_record(self):

        QMessageBox.information(
            self,
            "New Record",
            "Open create record dialog here."
        )
