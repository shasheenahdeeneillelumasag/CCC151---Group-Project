from models.patient import Patient
from repositories.base_repository import BaseRepository


class PatientRepository(BaseRepository):

    def create(self, patient: Patient):

        self.execute("""
            INSERT INTO patient (
                patient_id,
                first_name,
                last_name,
                birthdate,
                sex
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            patient.patient_id,
            patient.first_name,
            patient.last_name,
            patient.birthdate,
            patient.sex
        ))

    def get_by_id(
        self,
        patient_id: str
    ) -> Patient | None:

        row = self.fetch_one("""
            SELECT *
            FROM patient
            WHERE patient_id = ?
        """, (patient_id,))

        if row:
            return Patient(**row)

        return None

    def get_all(self) -> list[Patient]:

        rows = self.fetch_all("""
            SELECT *
            FROM patient
            ORDER BY last_name
        """)

        return [
            Patient(**row)
            for row in rows
        ]

    def update(self, patient: Patient):

        self.execute("""
            UPDATE patient
            SET
                first_name = ?,
                last_name = ?,
                birthdate = ?,
                sex = ?
            WHERE patient_id = ?
        """, (
            patient.first_name,
            patient.last_name,
            patient.birthdate,
            patient.sex,
            patient.patient_id
        ))

    def delete(self, patient_id: str):

        self.execute("""
            DELETE FROM patient
            WHERE patient_id = ?
        """, (patient_id,))
