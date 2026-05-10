from models.visit_record import VisitRecord
from repositories.base_repository import BaseRepository


class VisitRecordRepository(BaseRepository):

    def create(self, record: VisitRecord):

        self.execute("""
            INSERT INTO visit_record (
                record_id,
                visit_date,
                weight_kg,
                blood_pressure,
                patient_id
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            record.record_id,
            record.visit_date,
            record.weight_kg,
            record.blood_pressure,
            record.patient_id
        ))

    def get_by_id(
        self,
        record_id: str
    ) -> VisitRecord | None:

        row = self.fetch_one("""
            SELECT *
            FROM visit_record
            WHERE record_id = ?
        """, (record_id,))

        if row:
            return VisitRecord(**row)

        return None

    def get_by_patient(
        self,
        patient_id: str
    ) -> list[VisitRecord]:

        rows = self.fetch_all("""
            SELECT *
            FROM visit_record
            WHERE patient_id = ?
            ORDER BY visit_date DESC
        """, (patient_id,))

        return [
            VisitRecord(**row)
            for row in rows
        ]

    def delete(self, record_id: str):

        self.execute("""
            DELETE FROM visit_record
            WHERE record_id = ?
        """, (record_id,))
