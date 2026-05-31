from repositories.base_repository import BaseRepository
from models.visit_record import VisitRecord


class VisitRecordRepository(BaseRepository):

    def create(self, visit_record: VisitRecord) -> VisitRecord:

        record_id = self.execute_returning_id("""
            INSERT INTO visit_record (
                record_code,
                visit_date,
                weight_kg,
                blood_pressure,
                patient_id
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            "",
            visit_record.visit_date,
            visit_record.weight_kg,
            visit_record.blood_pressure,
            visit_record.patient_id
        ))

        record_code = f"R{record_id:03d}"

        self.execute("""
            UPDATE visit_record
            SET record_code = ?
            WHERE record_id = ?
        """, (
            record_code,
            record_id
        ))

        visit_record.record_id = record_id
        visit_record.record_code = record_code

        return visit_record

    def get_by_id(
        self,
        record_id: int
    ) -> VisitRecord | None:

        row = self.fetch_one("""
            SELECT *
            FROM visit_record
            WHERE record_id = ?
        """, (record_id,))

        if not row:
            return None

        return self._map_row(row)

    def get_all(self) -> list[VisitRecord]:

        rows = self.fetch_all("""
            SELECT *
            FROM visit_record
            ORDER BY visit_date DESC
        """)

        return [self._map_row(row) for row in rows]

    def get_by_patient_id(
        self,
        patient_id: int
    ) -> list[VisitRecord]:

        rows = self.fetch_all("""
            SELECT *
            FROM visit_record
            WHERE patient_id = ?
            ORDER BY visit_date DESC
        """, (patient_id,))

        return [self._map_row(row) for row in rows]

    def delete(self, record_id: int):

        self.execute("""
            DELETE FROM visit_record
            WHERE record_id = ?
        """, (record_id,))

    def update(self, visit_record: VisitRecord) -> VisitRecord:

        if visit_record.record_id is None:
            raise ValueError("record_id cannot be None for update")

        self.execute("""
            UPDATE visit_record
            SET
                visit_date = ?,
                weight_kg = ?,
                blood_pressure = ?,
                patient_id = ?
            WHERE record_id = ?
        """, (
            visit_record.visit_date,
            visit_record.weight_kg,
            visit_record.blood_pressure,
            visit_record.patient_id,
            visit_record.record_id
        ))

        return self.get_by_id(visit_record.record_id)

    @staticmethod
    def _map_row(row) -> VisitRecord:

        return VisitRecord(
            record_id=row["record_id"],
            record_code=row["record_code"],
            visit_date=row["visit_date"],
            weight_kg=row["weight_kg"],
            blood_pressure=row["blood_pressure"],
            patient_id=row["patient_id"]
        )

    def search(
        self,
        keyword: str
    ) -> list[VisitRecord]:

        keyword = f"%{keyword}%"

        rows = self.fetch_all("""
            SELECT *
            FROM visit_record
            WHERE record_code LIKE ?
            ORDER BY visit_date DESC
        """, (keyword,))

        return [self._map_row(row) for row in rows]

    def get_by_code(
        self,
        record_code: str
    ) -> VisitRecord | None:

        row = self.fetch_one("""
            SELECT *
            FROM visit_record
            WHERE record_code = ?
        """, (record_code,))

        if not row:
            return None

        return self._map_row(row)
