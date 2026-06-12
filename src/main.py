import os
import sys

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

from database.init_db import init_db
from login_window import AuthWindow
from services.user_service import UserService

ASSETS_DIR = os.path.join(os.path.dirname(__file__), '..', 'assets')


def main():
    init_db()
    UserService().init_users_table()
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    chevron_path = os.path.join(ASSETS_DIR, 'chevron_down.svg').replace('\\', '/')
    app.setStyleSheet(f"""
        QComboBox::down-arrow {{
            image: url({chevron_path});
            width: 12px;
            height: 12px;
        }}
        QComboBox::drop-down {{
            border: none;
            border-left: 1px solid #C8D9D2;
            width: 32px;
        }}
    """)

    icon_path = os.path.join(ASSETS_DIR, 'logo.png')
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    auth = AuthWindow()
    auth.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
