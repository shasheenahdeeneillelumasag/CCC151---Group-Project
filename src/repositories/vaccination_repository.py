from datetime import date
from models.vaccination_shot import VaccinationShot
from repositories.base_repository import BaseRepository


class VaccinationRepository(BaseRepository):

    def create(
        self,
        vaccination: VaccinationShot
    ) -> None:

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

        return (
            VaccinationShot(**row)
            if row else None
        )

    def get_by_patient(
        self,
        patient_id: str
    ) -> list[VaccinationShot]:

        rows = self.fetch_all("""
            SELECT *
            FROM vaccination_shots
            WHERE patient_id = ?
            ORDER BY schedule_date ASC
        """, (patient_id,))

        return [
            VaccinationShot(**row)
            for row in rows
        ]

    def get_by_status(
        self,
        status: str
    ) -> list[VaccinationShot]:

        rows = self.fetch_all("""
            SELECT *
            FROM vaccination_shots
            WHERE status = ?
            ORDER BY schedule_date ASC
        """, (status,))

        return [
            VaccinationShot(**row)
            for row in rows
        ]

    def get_overdue(
        self
    ) -> list[VaccinationShot]:

        rows = self.fetch_all("""
            SELECT *
            FROM vaccination_shots
            WHERE status = 'Pending'
            AND schedule_date < ?
            ORDER BY schedule_date ASC
        """, (date.today(),))

        return [
            VaccinationShot(**row)
            for row in rows
        ]

    def update(
        self,
        vaccination: VaccinationShot
    ) -> None:

        self.execute("""
            UPDATE vaccination_shots
            SET
                vaccination_name = ?,
                date_administered = ?,
                facility = ?,
                dose_number = ?,
                schedule_date = ?,
                status = ?,
                patient_id = ?
            WHERE vaccine_id = ?
        """, (
            vaccination.vaccination_name,
            vaccination.date_administered,
            vaccination.facility,
            vaccination.dose_number,
            vaccination.schedule_date,
            vaccination.status,
            vaccination.patient_id,
            vaccination.vaccine_id
        ))

    def update_status(
        self,
        vaccine_id: str,
        status: str
    ) -> None:

        self.execute("""
            UPDATE vaccination_shots
            SET status = ?
            WHERE vaccine_id = ?
        """, (
            status,
            vaccine_id
        ))

    def delete(
        self,
        vaccine_id: str
    ) -> None:

        self.execute("""
            DELETE FROM vaccination_shots
            WHERE vaccine_id = ?
        """, (vaccine_id,))
