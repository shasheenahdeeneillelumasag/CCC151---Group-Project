from repositories.base_repository import BaseRepository
from models.vaccination_shot import VaccinationShot


class VaccinationShotRepository(BaseRepository):

    def create(
        self,
        vaccination_shot: VaccinationShot
    ) -> VaccinationShot:

        vaccine_id = self.execute_returning_id("""
            INSERT INTO vaccination_shots (
                vaccine_code,
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
            "",
            vaccination_shot.vaccination_name,
            vaccination_shot.date_administered,
            vaccination_shot.facility,
            vaccination_shot.dose_number,
            vaccination_shot.schedule_date,
            vaccination_shot.status,
            vaccination_shot.patient_id
        ))

        vaccine_code = f"V{vaccine_id:03d}"

        self.execute("""
            UPDATE vaccination_shots
            SET vaccine_code = ?
            WHERE vaccine_id = ?
        """, (
            vaccine_code,
            vaccine_id
        ))

        vaccination_shot.vaccine_id = vaccine_id
        vaccination_shot.vaccine_code = vaccine_code

        return vaccination_shot

    def get_by_id(
        self,
        vaccine_id: int
    ) -> VaccinationShot | None:

        row = self.fetch_one("""
            SELECT *
            FROM vaccination_shots
            WHERE vaccine_id = ?
        """, (vaccine_id,))

        if not row:
            return None

        return self._map_row(row)

    def get_by_code(
        self,
        vaccine_code: str
    ) -> VaccinationShot | None:

        row = self.fetch_one("""
            SELECT *
            FROM vaccination_shots
            WHERE vaccine_code = ?
        """, (vaccine_code,))

        if not row:
            return None

        return self._map_row(row)

    def get_all(self) -> list[VaccinationShot]:

        rows = self.fetch_all("""
            SELECT *
            FROM vaccination_shots
            ORDER BY date_administered DESC
        """)

        return [self._map_row(row) for row in rows]

    def get_by_patient_id(
        self,
        patient_id: int
    ) -> list[VaccinationShot]:

        rows = self.fetch_all("""
            SELECT *
            FROM vaccination_shots
            WHERE patient_id = ?
            ORDER BY date_administered DESC
        """, (patient_id,))

        return [self._map_row(row) for row in rows]

    def update(
        self,
        vaccination_shot: VaccinationShot
    ) -> VaccinationShot:

        if vaccination_shot.vaccine_id is None:
            raise ValueError(
                "vaccine_id cannot be None for update"
            )

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
            vaccination_shot.vaccination_name,
            vaccination_shot.date_administered,
            vaccination_shot.facility,
            vaccination_shot.dose_number,
            vaccination_shot.schedule_date,
            vaccination_shot.status,
            vaccination_shot.patient_id,
            vaccination_shot.vaccine_id
        ))

        return self.get_by_id(vaccination_shot.vaccine_id)

    def delete(
        self,
        vaccine_id: int
    ):

        self.execute("""
            DELETE FROM vaccination_shots
            WHERE vaccine_id = ?
        """, (vaccine_id,))

    def search(
        self,
        keyword: str
    ) -> list[VaccinationShot]:

        keyword = f"%{keyword}%"

        rows = self.fetch_all("""
            SELECT *
            FROM vaccination_shots
            WHERE
                vaccine_code LIKE ?
                OR vaccination_name LIKE ?
                OR facility LIKE ?
                OR status LIKE ?
            ORDER BY date_administered DESC
        """, (
            keyword,
            keyword,
            keyword,
            keyword
        ))

        return [self._map_row(row) for row in rows]

    @staticmethod
    def _map_row(row) -> VaccinationShot:

        return VaccinationShot(
            vaccine_id=row["vaccine_id"],
            vaccine_code=row["vaccine_code"],
            vaccination_name=row["vaccination_name"],
            date_administered=row["date_administered"],
            facility=row["facility"],
            dose_number=row["dose_number"],
            schedule_date=row["schedule_date"],
            status=row["status"],
            patient_id=row["patient_id"]
        )
