from models.patient_contact import PatientContact
from repositories.base_repository import BaseRepository


class PatientContactRepository(BaseRepository):

    def add_contact(
        self,
        patient_id: str,
        contact_number: str
    ):

        self.execute("""
            INSERT INTO patient_contact (
                patient_id,
                contact_number
            )
            VALUES (?, ?)
        """, (
            patient_id,
            contact_number
        ))

    def get_by_patient(
        self,
        patient_id: str
    ) -> list[PatientContact]:

        rows = self.fetch_all("""
            SELECT *
            FROM patient_contact
            WHERE patient_id = ?
        """, (patient_id,))

        return [
            PatientContact(**row)
            for row in rows
        ]
