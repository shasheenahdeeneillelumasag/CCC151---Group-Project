import sys
from PyQt6.QtWidgets import QApplication

from pages.page_profile import PageProfile

app = QApplication(sys.argv)

window = PageProfile(patient_id=1)

window.show()

sys.exit(app.exec())
