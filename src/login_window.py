import os
import sys

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QStackedWidget, QFrame, QSizePolicy,
    QMessageBox
)
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QBrush, QColor, QFont
from PyQt6.QtCore import Qt, QSize, pyqtSignal

ASSETS_DIR = os.path.join(os.path.dirname(__file__), '..', 'assets')

def _user_service():
    from services.user_service import UserService
    return UserService()
PRIMARY      = "#1A9E78"
PRIMARY_DARK = "#157A5E"
SURFACE      = "#F2F7F5"
WHITE        = "#FFFFFF"
TEXT_MAIN    = "#1C2B27"
TEXT_MUTED   = "#6B8C85"
BORDER       = "#C8DDD9"
ERROR        = "#D94F4F"


class HealthField(QLineEdit):
    def __init__(self, placeholder="", password=False, parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        if password:
            self.setEchoMode(QLineEdit.EchoMode.Password)
        self.setMinimumHeight(44)
        self.setStyleSheet(f"""
            QLineEdit {{
                background: {WHITE};
                border: 1.5px solid {BORDER};
                border-radius: 10px;
                padding: 0 14px;
                font-size: 14px;
                color: {TEXT_MAIN};
            }}
            QLineEdit:focus {{
                border: 1.5px solid {PRIMARY};
            }}
            QLineEdit::placeholder {{
                color: {TEXT_MUTED};
            }}
        """)

    def mark_error(self, has_error: bool):
        c = ERROR if has_error else BORDER
        fc = ERROR if has_error else PRIMARY
        self.setStyleSheet(f"""
            QLineEdit {{
                background: {WHITE};
                border: 1.5px solid {c};
                border-radius: 10px;
                padding: 0 14px;
                font-size: 14px;
                color: {TEXT_MAIN};
            }}
            QLineEdit:focus {{ border: 1.5px solid {fc}; }}
        """)


class PrimaryButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setMinimumHeight(46)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(f"""
            QPushButton {{
                background: {PRIMARY};
                color: {WHITE};
                border: none;
                border-radius: 10px;
                font-size: 15px;
                font-weight: 600;
            }}
            QPushButton:hover {{ background: {PRIMARY_DARK}; }}
            QPushButton:pressed {{ background: #0F6650; }}
        """)


class LinkButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFlat(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {PRIMARY};
                border: none;
                font-size: 13px;
                font-weight: 600;
                padding: 0;
            }}
            QPushButton:hover {{ color: {PRIMARY_DARK}; text-decoration: underline; }}
        """)


def field_label(text):
    lbl = QLabel(text)
    lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 12px; font-weight: 600;")
    return lbl

class LoginForm(QWidget):
    login_requested  = pyqtSignal(str, str)
    signup_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background: {SURFACE};")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        center = QHBoxLayout()
        outer.addLayout(center)

        card = QWidget()
        card.setFixedWidth(400)
        card.setStyleSheet(f"background: {SURFACE};")
        center.addStretch()
        center.addWidget(card)
        center.addStretch()

        lay = QVBoxLayout(card)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        logo_row = QHBoxLayout()
        logo_row.setSpacing(10)
        logo_img = QLabel()
        logo_path = os.path.join(ASSETS_DIR, "logo.png")
        if os.path.exists(logo_path):
            pix = QPixmap(logo_path).scaled(36, 36, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_img.setPixmap(pix)
        logo_name = QLabel("HealthLink")
        logo_name.setStyleSheet(f"color: {PRIMARY}; font-size: 22px; font-weight: 700; letter-spacing: -0.3px;")
        logo_row.addWidget(logo_img)
        logo_row.addWidget(logo_name)
        logo_row.addStretch()
        lay.addLayout(logo_row)
        lay.addSpacing(28)

        heading = QLabel("Sign in")
        heading.setStyleSheet(f"color: {TEXT_MAIN}; font-size: 26px; font-weight: 700; letter-spacing: -0.4px;")
        sub = QLabel("Enter your credentials to continue")
        sub.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 13px;")
        lay.addWidget(heading)
        lay.addSpacing(4)
        lay.addWidget(sub)
        lay.addSpacing(28)

        self.username_field = HealthField("Enter username")
        self.password_field = HealthField("Enter password", password=True)

        lay.addWidget(field_label("Username"))
        lay.addSpacing(5)
        lay.addWidget(self.username_field)
        lay.addSpacing(16)
        lay.addWidget(field_label("Password"))
        lay.addSpacing(5)
        lay.addWidget(self.password_field)

        forgot_row = QHBoxLayout()
        forgot_row.addStretch()
        self.btn_forgot = LinkButton("Forgot password?")
        forgot_row.addWidget(self.btn_forgot)
        lay.addSpacing(6)
        lay.addLayout(forgot_row)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet(f"color: {ERROR}; font-size: 12px;")
        self.error_label.setWordWrap(True)
        self.error_label.hide()
        lay.addSpacing(6)
        lay.addWidget(self.error_label)

        lay.addSpacing(20)
        self.btn_login = PrimaryButton("Sign in")
        lay.addWidget(self.btn_login)

        lay.addSpacing(20)
        row = QHBoxLayout()
        row.addWidget(QLabel("Don't have an account?", styleSheet=f"color:{TEXT_MUTED}; font-size:13px;"))
        row.addSpacing(4)
        self.btn_go_signup = LinkButton("Create one")
        row.addWidget(self.btn_go_signup)
        row.addStretch()
        lay.addLayout(row)

        self.btn_login.clicked.connect(self._on_login)
        self.btn_go_signup.clicked.connect(self.signup_requested)
        self.btn_forgot.clicked.connect(self._on_forgot)
        self.username_field.returnPressed.connect(lambda: self.password_field.setFocus())
        self.password_field.returnPressed.connect(self._on_login)

    def show_error(self, message: str):
        """Display an error banner (called externally, e.g. from AuthWindow)."""
        self.error_label.setText(message)
        self.error_label.show()

    def _on_login(self):
        u = self.username_field.text().strip()
        p = self.password_field.text()
        self.username_field.mark_error(not u)
        self.password_field.mark_error(not p)
        if not u or not p:
            self.error_label.setText("Please fill in all fields.")
            self.error_label.show()
            return
        self.error_label.hide()
        self.login_requested.emit(u, p)

    def _on_forgot(self):
        QMessageBox.information(
            self, "Reset password",
            "Please contact your healthcare provider or system administrator\n"
            "to reset your password."
        )

class SignUpForm(QWidget):
    signup_requested = pyqtSignal(dict)
    login_requested  = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background: {SURFACE};")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        card = QWidget()
        card.setFixedWidth(400)
        card.setStyleSheet(f"background: {SURFACE};")
        center = QHBoxLayout()
        center.setContentsMargins(0, 0, 0, 0)
        center.addStretch()
        center.addWidget(card)
        center.addStretch()
        outer.addLayout(center)

        lay = QVBoxLayout(card)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        logo_row = QHBoxLayout()
        logo_row.setSpacing(10)
        logo_img = QLabel()
        logo_path = os.path.join(ASSETS_DIR, "logo.png")
        if os.path.exists(logo_path):
            pix = QPixmap(logo_path).scaled(36, 36, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_img.setPixmap(pix)
        logo_name = QLabel("HealthLink")
        logo_name.setStyleSheet(f"color: {PRIMARY}; font-size: 22px; font-weight: 700; letter-spacing: -0.3px;")
        logo_row.addWidget(logo_img)
        logo_row.addWidget(logo_name)
        logo_row.addStretch()
        lay.addLayout(logo_row)
        lay.addSpacing(28)

        heading = QLabel("Create account")
        heading.setStyleSheet(f"color: {TEXT_MAIN}; font-size: 26px; font-weight: 700; letter-spacing: -0.4px;")
        sub = QLabel("Register to start managing your health records")
        sub.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 13px;")
        lay.addWidget(heading)
        lay.addSpacing(4)
        lay.addWidget(sub)
        lay.addSpacing(28)

        lay.addWidget(field_label("Full name"))
        lay.addSpacing(5)
        name_row = QHBoxLayout()
        name_row.setSpacing(10)
        self.first_name = HealthField("First name")
        self.last_name  = HealthField("Last name")
        name_row.addWidget(self.first_name)
        name_row.addWidget(self.last_name)
        lay.addLayout(name_row)
        lay.addSpacing(16)

        self.email_field    = HealthField("email@example.com")
        self.username_field = HealthField("Choose a username")
        self.password_field = HealthField("Password (min. 8 characters)", password=True)
        self.confirm_field  = HealthField("Confirm password", password=True)

        for lbl, widget in [
            ("Email address",    self.email_field),
            ("Username",         self.username_field),
            ("Password",         self.password_field),
            ("Confirm password", self.confirm_field),
        ]:
            lay.addWidget(field_label(lbl))
            lay.addSpacing(5)
            lay.addWidget(widget)
            lay.addSpacing(16)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet(f"color: {ERROR}; font-size: 12px;")
        self.error_label.setWordWrap(True)
        self.error_label.hide()
        lay.addWidget(self.error_label)
        lay.addSpacing(8)

        self.btn_signup = PrimaryButton("Create account")
        lay.addWidget(self.btn_signup)
        lay.addSpacing(20)

        row = QHBoxLayout()
        row.addWidget(QLabel("Already have an account?", styleSheet=f"color:{TEXT_MUTED}; font-size:13px;"))
        row.addSpacing(4)
        self.btn_go_login = LinkButton("Sign in")
        row.addWidget(self.btn_go_login)
        row.addStretch()
        lay.addLayout(row)

        self.btn_signup.clicked.connect(self._on_signup)
        self.btn_go_login.clicked.connect(self.login_requested)

    def show_error(self, message: str):
        """Display an error banner (called externally, e.g. from AuthWindow)."""
        self.error_label.setText(message)
        self.error_label.show()

    def _on_signup(self):
        fields = {
            "first_name": self.first_name.text().strip(),
            "last_name":  self.last_name.text().strip(),
            "email":      self.email_field.text().strip(),
            "username":   self.username_field.text().strip(),
            "password":   self.password_field.text(),
            "confirm":    self.confirm_field.text(),
        }
        for w in [self.first_name, self.last_name, self.email_field,
                  self.username_field, self.password_field, self.confirm_field]:
            w.mark_error(False)
        self.error_label.hide()

        errors = []
        if not fields["first_name"]:  self.first_name.mark_error(True);    errors.append("First name is required.")
        if not fields["last_name"]:   self.last_name.mark_error(True);     errors.append("Last name is required.")
        if not fields["email"] or "@" not in fields["email"]:
            self.email_field.mark_error(True); errors.append("A valid email address is required.")
        if not fields["username"]:    self.username_field.mark_error(True); errors.append("Username is required.")
        if len(fields["password"]) < 8:
            self.password_field.mark_error(True); errors.append("Password must be at least 8 characters.")
        if fields["password"] != fields["confirm"]:
            self.confirm_field.mark_error(True); errors.append("Passwords do not match.")

        if errors:
            self.error_label.setText(errors[0])
            self.error_label.show()
            return

        self.signup_requested.emit(fields)

class AuthWindow(QMainWindow):
    authenticated = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("HealthLink — Sign in")
        self.setFixedSize(560, 600)

        root = QWidget()
        root.setStyleSheet(f"background: {SURFACE};")
        self.setCentralWidget(root)

        root_lay = QVBoxLayout(root)
        root_lay.setContentsMargins(80, 60, 80, 60)

        self.stack = QStackedWidget()
        self.stack.setStyleSheet(f"background: {SURFACE};")
        root_lay.addWidget(self.stack)

        self.login_form  = LoginForm()
        self.signup_form = SignUpForm()
        self.stack.addWidget(self.login_form)  
        self.stack.addWidget(self.signup_form) 

        self.login_form.signup_requested.connect(lambda: self._switch(1))
        self.signup_form.login_requested.connect(lambda: self._switch(0))
        self.login_form.login_requested.connect(self._handle_login)
        self.signup_form.signup_requested.connect(self._handle_signup)

        self.stack.setCurrentIndex(0)

    def _switch(self, index: int):
        self.stack.setCurrentIndex(index)
        self.setFixedSize(560, 700 if index == 1 else 600)

    def _handle_login(self, username: str, password: str):
        user = _user_service().login(username, password)
        if user is None:
            self.login_form.show_error("Incorrect username or password.")
            return
        from core.app_settings import AppSettings
        AppSettings().set_active_patient_code(user.patient_code or "")
        self.authenticated.emit(user.username)
        self._open_main_app(user)

    def _handle_signup(self, data: dict):
        svc = _user_service()
        ok, error = svc.register(
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"],
            username=data["username"],
            password=data["password"],
        )
        if not ok:
            self.signup_form.show_error(error)
            return

        from services.patient_service import PatientService
        patient = PatientService().register_patient(
            first_name=data["first_name"],
            last_name=data["last_name"],
            birthdate="2000-01-01",
            sex="Male",
        )
        svc.link_patient(data["username"], patient.patient_code)

        QMessageBox.information(
            self, "Account created",
            f"Welcome, {data['first_name']}!\n\nYour account has been created. You can now sign in.",
        )
        self._switch(0)
        self.login_form.username_field.setText(data["username"])

    def _open_main_app(self, user):
        """Opens the main HealthLink window and closes the auth window."""
        from main_window import MainWindow
        self.main_window = MainWindow(user=user)
        self.main_window.show()
        self.close()


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = AuthWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()