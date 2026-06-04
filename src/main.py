import sys
from PyQt6.QtWidgets import QApplication

from pages.page_profile import PageProfile
from pages.page_records import PageRecords
from pages.page_documents import PageDocuments
from pages.page_vaccination import PageVaccinations

from core.app_settings import AppSettings

settings = AppSettings()

app = QApplication(sys.argv)

patient_code = settings.get_active_patient_code()

if not patient_code:
    settings.set_active_patient_code(
    "P001"        
    )


window = PageVaccinations()

window.show()

sys.exit(app.exec())
