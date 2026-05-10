from models.prescription import Prescription
from repositories.base_repository import BaseRepository


class PrescriptionRepository(BaseRepository):

    def create(self, prescription: Prescription):

        self.execute("""
            INSERT INTO prescription (
                prescription_id,
                medication_name,
                dosage,
                prescribed_date,
                prescribed_by,
                record_id
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            prescription.prescription_id,
            prescription.medication_name,
            prescription.dosage,
            prescription.prescribed_date,
            prescription.prescribed_by,
            prescription.record_id
        ))

    def get_by_record(
        self,
        record_id: str
    ) -> list[Prescription]:

        rows = self.fetch_all("""
            SELECT *
            FROM prescription
            WHERE record_id = ?
            ORDER BY prescribed_date DESC
        """, (record_id,))

        return [
            Prescription(**row)
            for row in rows
        ]

    def delete(self, prescription_id: str):

        self.execute("""
            DELETE FROM prescription
            WHERE prescription_id = ?
        """, (prescription_id,))
