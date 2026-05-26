from repositories.patient_contact_repository import (
    PatientContactRepository
)

from models.patient_contact import PatientContact


class PatientContactService:

    def __init__(self):
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

        return self.repo.create(contact)

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

        return self.repo.update(contact)

    def delete_contact(
        self,
        contact_id: int
    ):

        self.repo.delete(contact_id)
