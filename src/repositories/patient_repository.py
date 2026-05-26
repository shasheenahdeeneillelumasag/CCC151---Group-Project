from repositories.base_repository import BaseRepository
from models.patient import Patient

class PatientRepository(BaseRepository):

    def create(self, patient: Patient) -> Patient:

        patient_id = self.execute_returning_id("""
            INSERT INTO patient (
                patient_code,
                first_name,
                last_name,
                birthdate,
                sex
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            "",
            patient.first_name,
            patient.last_name,
            patient.birthdate,
            patient.sex
        ))

        patient_code = f"P{patient_id:03d}"

        self.execute("""
            UPDATE patient
            SET patient_code = ?
            WHERE patient_id = ?
        """, (
            patient_code,
            patient_id
        ))

        patient.patient_id = patient_id
        patient.patient_code = patient_code

        return patient

    def get_by_id(
        self,
        patient_id: int
    ) -> Patient | None:

        row = self.fetch_one("""
            SELECT *
            FROM patient
            WHERE patient_id = ?
        """, (patient_id,))

        if not row:
            return None

        return self._map_row(row)

    def get_by_code(
        self,
        patient_code: str
    ) -> Patient | None:

        row = self.fetch_one("""
            SELECT *
            FROM patient
            WHERE patient_code = ?
        """, (patient_code,))

        if not row:
            return None

        return self._map_row(row)

    def get_all(self) -> list[Patient]:

        rows = self.fetch_all("""
            SELECT *
            FROM patient
            ORDER BY last_name
        """)

        return [self._map_row(row) for row in rows]

    def search(
        self,
        keyword: str
    ) -> list[Patient]:

        keyword = f"%{keyword}%"

        rows = self.fetch_all("""
            SELECT *
            FROM patient
            WHERE
                patient_code LIKE ?
                OR first_name LIKE ?
                OR last_name LIKE ?
        """, (
            keyword,
            keyword,
            keyword
        ))

        return [self._map_row(row) for row in rows]

    def delete(self, patient_id: int):

        self.execute("""
            DELETE FROM patient
            WHERE patient_id = ?
        """, (patient_id,))

    @staticmethod
    def _map_row(row) -> Patient:

        return Patient(
            patient_id=row["patient_id"],
            patient_code=row["patient_code"],
            first_name=row["first_name"],
            last_name=row["last_name"],
            birthdate=row["birthdate"],
            sex=row["sex"]
        )
    
    def update(self, patient: Patient) -> Patient:

        if patient.patient_id is None:
            raise ValueError("patient_id cannot be None for update")

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

        return self.get_by_id(patient.patient_id)
