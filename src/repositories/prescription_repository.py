from repositories.base_repository import BaseRepository
from models.prescription import Prescription

class PrescriptionRepository(BaseRepository):

    def _generate_code(self) -> str:

        row = self.fetch_one("""
            SELECT prescription_code
            FROM prescription
            ORDER BY prescription_id DESC
            LIMIT 1
        """)

        if row:
            next_num = int(row["prescription_code"][2:]) + 1
        else:
            next_num = 1

        return f"RX{next_num:03d}"

    def create(
        self,
        prescription: Prescription
    ) -> Prescription:

        code = self._generate_code()

        prescription_id = self.execute_returning_id("""
            INSERT INTO prescription (
                prescription_code,
                medication_name,
                dosage,
                prescribed_date,
                prescribed_by,
                record_id
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            code,
            prescription.medication_name,
            prescription.dosage,
            prescription.prescribed_date,
            prescription.prescribed_by,
            prescription.record_id
        ))

        prescription.prescription_id = prescription_id
        prescription.prescription_code = code

        return prescription

    def get_by_id(
        self,
        prescription_id: int
    ) -> Prescription | None:

        row = self.fetch_one("""
            SELECT *
            FROM prescription
            WHERE prescription_id = ?
        """, (prescription_id,))

        return Prescription(**row) if row else None

    def get_all(self) -> list[Prescription]:

        rows = self.fetch_all("""
            SELECT *
            FROM prescription
            ORDER BY prescribed_date DESC
        """)

        return [Prescription(**row) for row in rows]

    def get_by_record_id(
        self,
        record_id: int
    ) -> list[Prescription]:

        rows = self.fetch_all("""
            SELECT *
            FROM prescription
            WHERE record_id = ?
            ORDER BY prescribed_date DESC
        """, (record_id,))

        return [Prescription(**row) for row in rows]

    def search(
        self,
        keyword: str
    ) -> list[Prescription]:

        pattern = f"%{keyword}%"

        rows = self.fetch_all("""
            SELECT *
            FROM prescription
            WHERE prescription_code LIKE ?
               OR medication_name LIKE ?
               OR prescribed_by LIKE ?
        """, (
            pattern,
            pattern,
            pattern
        ))

        return [Prescription(**row) for row in rows]

    def update(
        self,
        prescription: Prescription
    ):

        self.execute("""
            UPDATE prescription
            SET medication_name = ?,
                dosage = ?,
                prescribed_date = ?,
                prescribed_by = ?,
                record_id = ?
            WHERE prescription_id = ?
        """, (
            prescription.medication_name,
            prescription.dosage,
            prescription.prescribed_date,
            prescription.prescribed_by,
            prescription.record_id,
            prescription.prescription_id
        ))

    def delete(
        self,
        prescription_id: int
    ):

        self.execute("""
            DELETE FROM prescription
            WHERE prescription_id = ?
        """, (prescription_id,))

    def get_by_code(
        self,
        prescription_code: str
    ) -> Prescription | None:

        row = self.fetch_one("""
            SELECT *
            FROM prescription
            WHERE prescription_code = ?
        """, (prescription_code,))

        if not row:
            return None

        return self._map_row(row)
