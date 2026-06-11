from datetime import date

from PyQt6.QtWidgets import QComboBox, QCompleter
from PyQt6.QtCore import QDate, Qt


MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]


def init_date_picker(month_combo: QComboBox, day_combo: QComboBox, year_combo: QComboBox):
    month_combo.addItems(MONTHS)
    month_combo.setCompleter(QCompleter(MONTHS, month_combo.parent()))
    month_combo.completer().setFilterMode(Qt.MatchFlag.MatchContains)

    days = [str(d) for d in range(1, 32)]
    day_combo.addItems(days)
    day_combo.setCompleter(QCompleter(days, day_combo.parent()))

    current_year = date.today().year
    years = [str(y) for y in range(1900, current_year + 1)]
    year_combo.addItems(years)
    year_combo.setCompleter(QCompleter(years, year_combo.parent()))


def set_date_picker(month_combo, day_combo, year_combo, dt: QDate):
    month_combo.setCurrentText(dt.toString("MMMM"))
    day_combo.setCurrentText(dt.toString("d"))
    year_combo.setCurrentText(dt.toString("yyyy"))


def get_date_from_picker(month_combo, day_combo, year_combo) -> QDate:
    month = month_combo.currentIndex() + 1
    day = int(day_combo.currentText())
    year = int(year_combo.currentText())
    return QDate(year, month, day)


def get_date_str_from_picker(month_combo, day_combo, year_combo) -> str:
    month = month_combo.currentIndex() + 1
    day = int(day_combo.currentText())
    year = int(year_combo.currentText())
    return f"{year}-{month:02d}-{day:02d}"
