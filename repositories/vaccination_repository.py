from models.vaccination_shot import VaccinationShot
from repositories.base_repository import BaseRepository


class VaccinationRepository(BaseRepository):

    def create(self, vaccination: VaccinationShot):

        self.execute("""
            INSERT INTO vaccination_shots (
                vaccine_id,
                vaccination_name,
                date_administered,
                facility,
                dose_number,
                schedule_date,
                status,
                patient_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            vaccination.vaccine_id,
            vaccination.vaccination_name,
            vaccination.date_administered,
            vaccination.facility,
            vaccination.dose_number,
            vaccination.schedule_date,
            vaccination.status,
            vaccination.patient_id
        ))

    def get_by_id(
        self,
        vaccine_id: str
    ) -> VaccinationShot | None:

        row = self.fetch_one("""
            SELECT *
            FROM vaccination_shots
            WHERE vaccine_id = ?
        """, (vaccine_id,))

        if row:
            return VaccinationShot(**row)

        return None

    def get_by_patient(
        self,
        patient_id: str
    ) -> list[VaccinationShot]:

        rows = self.fetch_all("""
            SELECT *
            FROM vaccination_shots
            WHERE patient_id = ?
            ORDER BY date_administered DESC
        """, (patient_id,))

        return [
            VaccinationShot(**row)
            for row in rows
        ]

    def update(self, vaccination: VaccinationShot):

        self.execute("""
            UPDATE vaccination_shots
            SET
                vaccination_name = ?,
                date_administered = ?,
                facility = ?,
                dose_number = ?,
                schedule_date = ?,
                status = ?
            WHERE vaccine_id = ?
        """, (
            vaccination.vaccination_name,
            vaccination.date_administered,
            vaccination.facility,
            vaccination.dose_number,
            vaccination.schedule_date,
            vaccination.status,
            vaccination.vaccine_id
        ))

    def delete(self, vaccine_id: str):

        self.execute("""
            DELETE FROM vaccination_shots
            WHERE vaccine_id = ?
        """, (vaccine_id,))
