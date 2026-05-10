from models.diagnosis import Diagnosis
from repositories.base_repository import BaseRepository


class DiagnosisRepository(BaseRepository):

    def create(self, diagnosis: Diagnosis):

        self.execute("""
            INSERT INTO diagnosis (
                diagnosis_id,
                diagnosis_name,
                description,
                diagnosed_date,
                record_id
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            diagnosis.diagnosis_id,
            diagnosis.diagnosis_name,
            diagnosis.description,
            diagnosis.diagnosed_date,
            diagnosis.record_id
        ))

    def get_by_record(
        self,
        record_id: str
    ) -> list[Diagnosis]:

        rows = self.fetch_all("""
            SELECT *
            FROM diagnosis
            WHERE record_id = ?
            ORDER BY diagnosed_date DESC
        """, (record_id,))

        return [
            Diagnosis(**row)
            for row in rows
        ]

    def delete(self, diagnosis_id: str):

        self.execute("""
            DELETE FROM diagnosis
            WHERE diagnosis_id = ?
        """, (diagnosis_id,))
