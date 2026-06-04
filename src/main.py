import sys
from PyQt6.QtWidgets import QApplication

from core.app_settings import AppSettings
from main_window import MainWindow

from pages.page_profile import PageProfile
from pages.page_records import PageRecords
from pages.page_documents import PageDocuments
from pages.page_vaccination import PageVaccinations
from pages.page_appointments import PageAppointments

def main():
    app = QApplication(sys.argv)
    
    settings = AppSettings()
    patient_code = settings.get_active_patient_code()

    if not patient_code:
        settings.set_active_patient_code("P001")

    # --- 2. GLOBAL MODERN STYLING ---
    modern_style = """
    /* Main Window and Dialog Backgrounds */
    QMainWindow, QDialog, QStackedWidget {
        background-color: #F3F4F6;
    }
    
    /* General Text Styling */
    QWidget {
        font-family: 'Segoe UI', Arial, sans-serif;
        color: #1F2937; 
        font-size: 14px;
    }
    
    /* Sidebar or Container Frames */
    QFrame {
        background-color: #FFFFFF;
        border-radius: 8px;
    }
    
    /* --- BUTTONS --- */
    QPushButton {
        background-color: #3B82F6; /* Modern Blue */
        color: white;
        border: none;
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #2563EB; /* Darker blue on hover */
    }
    
    /* THE FIX: Faded / Disabled Buttons */
    QPushButton:disabled {
        background-color: #E5E7EB; /* Light gray background */
        color: #9CA3AF; /* Muted gray text */
    }
    
    /* Input Fields */
    QLineEdit, QPlainTextEdit, QDateEdit, QComboBox {
        background-color: #FFFFFF;
        border: 1px solid #D1D5DB;
        border-radius: 4px;
        padding: 6px;
    }
    QLineEdit:focus, QPlainTextEdit:focus {
        border: 1px solid #3B82F6;
    }
    """
    
    app.setStyleSheet(modern_style)

    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()