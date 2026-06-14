from datetime import date

from PyQt6.QtWidgets import QComboBox, QCompleter
from PyQt6.QtCore import QDate, Qt


MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]


def _constrain_month(combo: QComboBox):
    le = combo.lineEdit()
    def _on_text(text: str):
        filtered = "".join(ch for ch in text if ch.isalpha() or ch.isspace())
        if filtered != text:
            le.blockSignals(True)
            le.setText(filtered)
            le.blockSignals(False)
    le.textChanged.connect(_on_text)


def _constrain_day(combo: QComboBox):
    le = combo.lineEdit()
    def _on_text(text: str):
        filtered = "".join(ch for ch in text if ch.isdigit())[:2]
        if filtered != text:
            le.blockSignals(True)
            le.setText(filtered)
            le.blockSignals(False)
    def _clamp():
        try:
            val = int(le.text())
            if val < 1:
                le.setText("1")
            elif val > 31:
                le.setText("31")
        except ValueError:
            pass
    le.textChanged.connect(_on_text)
    le.editingFinished.connect(_clamp)


def _constrain_year(combo: QComboBox):
    le = combo.lineEdit()
    def _on_text(text: str):
        filtered = "".join(ch for ch in text if ch.isdigit())[:4]
        if filtered != text:
            le.blockSignals(True)
            le.setText(filtered)
            le.blockSignals(False)
    le.textChanged.connect(_on_text)


def init_date_picker(month_combo: QComboBox, day_combo: QComboBox, year_combo: QComboBox):
    month_combo.addItems(MONTHS)
    month_combo.setCompleter(QCompleter(MONTHS, month_combo.parent()))
    month_combo.completer().setFilterMode(Qt.MatchFlag.MatchContains)
    _constrain_month(month_combo)

    days = [str(d) for d in range(1, 32)]
    day_combo.addItems(days)
    day_combo.setCompleter(QCompleter(days, day_combo.parent()))
    _constrain_day(day_combo)

    current_year = date.today().year
    years = [str(y) for y in range(1900, current_year + 1)]
    year_combo.addItems(years)
    year_combo.setCompleter(QCompleter(years, year_combo.parent()))
    _constrain_year(year_combo)


def set_date_picker(month_combo, day_combo, year_combo, dt: QDate):
    month_combo.setCurrentText(dt.toString("MMMM"))
    day_combo.setCurrentText(dt.toString("d"))
    year_combo.setCurrentText(dt.toString("yyyy"))


def _valid_date(month_combo, day_combo, year_combo) -> QDate | None:
    try:
        month = month_combo.currentIndex() + 1
        if month == 0:
            return None
        day = int(day_combo.currentText())
        year = int(year_combo.currentText())
        if not (1 <= day <= 31):
            return None
        if len(str(year)) != 4:
            return None
        d = QDate(year, month, day)
        return d if d.isValid() else None
    except (ValueError, TypeError):
        return None


def get_date_from_picker(month_combo, day_combo, year_combo) -> QDate:
    d = _valid_date(month_combo, day_combo, year_combo)
    if d is None:
        month = month_combo.currentIndex() + 1
        year = int(year_combo.currentText())
        d = QDate(year, month, 1)
        d = d.addDays(d.daysInMonth() - 1)
        day_combo.setCurrentText(str(d.day()))
    return d


def get_date_str_from_picker(month_combo, day_combo, year_combo) -> str:
    d = get_date_from_picker(month_combo, day_combo, year_combo)
    return f"{d.year()}-{d.month():02d}-{d.day():02d}"
