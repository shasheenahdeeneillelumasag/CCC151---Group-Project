from repositories.base_repository import BaseRepository
from models.patient_contact import PatientContact
from models.patient import Patient

class PatientContactRepository(BaseRepository):

    def create(self, contact: PatientContact) -> PatientContact:

        contact_id = self.execute_returning_id("""
            INSERT INTO patient_contact (
                patient_id,
                contact_number
            )
            VALUES (?, ?)
        """, (
            contact.patient_id,
            contact.contact_number
        ))

        contact.contact_id = contact_id

        return contact

    def get_by_id(
        self,
        contact_id: int
    ) -> PatientContact | None:

        row = self.fetch_one("""
            SELECT *
            FROM patient_contact
            WHERE contact_id = ?
        """, (contact_id,))

        if not row:
            return None

        return self._map_row(row)

    def get_all(self) -> list[PatientContact]:

        rows = self.fetch_all("""
            SELECT *
            FROM patient_contact
            ORDER BY contact_id
        """)

        return [self._map_row(row) for row in rows]

    def get_by_patient_id(
        self,
        patient_id: int
    ) -> list[PatientContact]:

        rows = self.fetch_all("""
            SELECT *
            FROM patient_contact
            WHERE patient_id = ?
            ORDER BY contact_id
        """, (patient_id,))

        return [self._map_row(row) for row in rows]

    def delete(self, contact_id: int):

        self.execute("""
            DELETE FROM patient_contact
            WHERE contact_id = ?
        """, (contact_id,))

    def update(
        self,
        contact: PatientContact
    ) -> PatientContact:

        if contact.contact_id is None:
            raise ValueError("contact_id cannot be None for update")

        self.execute("""
            UPDATE patient_contact
            SET
                patient_id = ?,
                contact_number = ?
            WHERE contact_id = ?
        """, (
            contact.patient_id,
            contact.contact_number,
            contact.contact_id
        ))

        return self.get_by_id(contact.contact_id)

    @staticmethod
    def _map_row(row) -> PatientContact:

        return PatientContact(
            contact_id=row["contact_id"],
            contact_number=row["contact_number"],
            patient_id=row["patient_id"]
        )
