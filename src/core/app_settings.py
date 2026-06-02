from PyQt6.QtCore import QSettings


class AppSettings:

    def __init__(self):
        self.settings = QSettings(
            "HealthLink",
        )

    def get_active_patient_code(self):
        return self.settings.value(
            "active_patient_code",
            None,
            type=str
        )

    def set_active_patient_code(self, patient_code):
        self.settings.setValue(
            "active_patient_code",
            patient_code
        )
