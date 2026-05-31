from repositories.base_repository import BaseRepository
from models.diagnosis import Diagnosis

class DiagnosisRepository(BaseRepository):

    def _generate_code(self) -> str:

        row = self.fetch_one("""
            SELECT diagnosis_code
            FROM diagnosis
            ORDER BY diagnosis_id DESC
            LIMIT 1
        """)

        if row:
            next_num = int(row["diagnosis_code"][1:]) + 1
        else:
            next_num = 1

        return f"D{next_num:03d}"

    def create(
        self,
        diagnosis: Diagnosis
    ) -> Diagnosis:

        code = self._generate_code()

        diagnosis_id = self.execute_returning_id("""
            INSERT INTO diagnosis (
                diagnosis_code,
                diagnosis_name,
                description,
                diagnosed_date,
                record_id
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            code,
            diagnosis.diagnosis_name,
            diagnosis.description,
            diagnosis.diagnosed_date,
            diagnosis.record_id
        ))

        diagnosis.diagnosis_id = diagnosis_id
        diagnosis.diagnosis_code = code

        return diagnosis

    def get_by_id(
        self,
        diagnosis_id: int
    ) -> Diagnosis | None:

        row = self.fetch_one("""
            SELECT *
            FROM diagnosis
            WHERE diagnosis_id = ?
        """, (diagnosis_id,))

        return Diagnosis(**row) if row else None

    def get_all(self) -> list[Diagnosis]:

        rows = self.fetch_all("""
            SELECT *
            FROM diagnosis
            ORDER BY diagnosed_date DESC
        """)

        return [Diagnosis(**row) for row in rows]

    def get_by_record_id(
        self,
        record_id: int
    ) -> list[Diagnosis]:

        rows = self.fetch_all("""
            SELECT *
            FROM diagnosis
            WHERE record_id = ?
            ORDER BY diagnosed_date DESC
        """, (record_id,))

        return [Diagnosis(**row) for row in rows]

    def search(
        self,
        keyword: str
    ) -> list[Diagnosis]:

        pattern = f"%{keyword}%"

        rows = self.fetch_all("""
            SELECT *
            FROM diagnosis
            WHERE diagnosis_code LIKE ?
               OR diagnosis_name LIKE ?
               OR description LIKE ?
        """, (
            pattern,
            pattern,
            pattern
        ))

        return [Diagnosis(**row) for row in rows]

    def update(
        self,
        diagnosis: Diagnosis
    ):

        self.execute("""
            UPDATE diagnosis
            SET diagnosis_name = ?,
                description = ?,
                diagnosed_date = ?,
                record_id = ?
            WHERE diagnosis_id = ?
        """, (
            diagnosis.diagnosis_name,
            diagnosis.description,
            diagnosis.diagnosed_date,
            diagnosis.record_id,
            diagnosis.diagnosis_id
        ))

    def delete(
        self,
        diagnosis_id: int
    ):

        self.execute("""
            DELETE FROM diagnosis
            WHERE diagnosis_id = ?
        """, (diagnosis_id,))

    def get_by_code(
        self,
        diagnosis_code: str
    ) -> Diagnosis | None:

        row = self.fetch_one("""
            SELECT *
            FROM diagnosis
            WHERE diagnosis_code = ?
        """, (diagnosis_code,))

        if not row:
            return None

        return self._map_row(row)
