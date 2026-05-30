import sys
from PyQt6.QtWidgets import QApplication

from pages.page_profile import PageProfile
from pages.page_records import PageRecords


app = QApplication(sys.argv)

window = PageRecords(patient_id=1)

window.show()

sys.exit(app.exec())
