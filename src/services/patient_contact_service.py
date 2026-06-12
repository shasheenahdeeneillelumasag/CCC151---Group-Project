from repositories.patient_contact_repository import (
    PatientContactRepository
)

from models.patient_contact import PatientContact
from PyQt6.QtCore import QObject, pyqtSignal


class PatientContactService(QObject):
    changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.repo = PatientContactRepository()

    def add_contact(
        self,
        patient_id: int,
        contact_number: str
    ) -> PatientContact:

        contact = PatientContact(
            contact_id=None,
            patient_id=patient_id,
            contact_number=contact_number
        )

        self.repo.create(contact)
        self.changed.emit()
        return contact

    def get_contact_by_id(
        self,
        contact_id: int
    ) -> PatientContact | None:

        return self.repo.get_by_id(contact_id)

    def get_all_contacts(self) -> list[PatientContact]:

        return self.repo.get_all()

    def get_contacts_by_patient_id(
        self,
        patient_id: int
    ) -> list[PatientContact]:

        return self.repo.get_by_patient_id(
            patient_id
        )

    def update_contact(
        self,
        contact_id: int,
        patient_id: int,
        contact_number: str
    ) -> PatientContact:

        contact = PatientContact(
            contact_id=contact_id,
            patient_id=patient_id,
            contact_number=contact_number
        )

        self.repo.update(contact)
        self.changed.emit()
        return contact

    def delete_contact(
        self,
        contact_id: int
    ):

        self.repo.delete(contact_id)
        self.changed.emit()
