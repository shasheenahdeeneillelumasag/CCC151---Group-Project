from repositories.base_repository import BaseRepository
from models.appointment import Appointment


class AppointmentRepository(BaseRepository):

    def create(self, appointment: Appointment) -> Appointment:

        appointment_id = self.execute_returning_id("""
            INSERT INTO appointment (
                appointment_code,
                appt_date,
                appt_time,
                purpose,
                clinic_name,
                status,
                patient_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            "",
            appointment.appt_date,
            appointment.appt_time,
            appointment.purpose,
            appointment.clinic_name,
            appointment.status,
            appointment.patient_id
        ))

        appointment_code = f"A{appointment_id:03d}"

        self.execute("""
            UPDATE appointment
            SET appointment_code = ?
            WHERE appointment_id = ?
        """, (
            appointment_code,
            appointment_id
        ))

        appointment.appointment_id = appointment_id
        appointment.appointment_code = appointment_code

        return appointment

    def get_by_id(
        self,
        appointment_id: int
    ) -> Appointment | None:

        row = self.fetch_one("""
            SELECT *
            FROM appointment
            WHERE appointment_id = ?
        """, (appointment_id,))

        if not row:
            return None

        return self._map_row(row)

    def get_all(self) -> list[Appointment]:

        rows = self.fetch_all("""
            SELECT *
            FROM appointment
            ORDER BY appt_date DESC, appt_time DESC
        """)

        return [self._map_row(row) for row in rows]

    def get_by_patient_id(
        self,
        patient_id: int
    ) -> list[Appointment]:

        rows = self.fetch_all("""
            SELECT *
            FROM appointment
            WHERE patient_id = ?
            ORDER BY appt_date DESC, appt_time DESC
        """, (patient_id,))

        return [self._map_row(row) for row in rows]

    def get_by_code(
        self,
        appointment_code: str
    ) -> Appointment | None:

        row = self.fetch_one("""
            SELECT *
            FROM appointment
            WHERE appointment_code = ?
        """, (appointment_code,))

        if not row:
            return None

        return self._map_row(row)

    def update(
        self,
        appointment: Appointment
    ) -> Appointment:

        if appointment.appointment_id is None:
            raise ValueError(
                "appointment_id cannot be None for update"
            )

        self.execute("""
            UPDATE appointment
            SET
                appt_date = ?,
                appt_time = ?,
                purpose = ?,
                clinic_name = ?,
                status = ?,
                patient_id = ?
            WHERE appointment_id = ?
        """, (
            appointment.appt_date,
            appointment.appt_time,
            appointment.purpose,
            appointment.clinic_name,
            appointment.status,
            appointment.patient_id,
            appointment.appointment_id
        ))

        return self.get_by_id(appointment.appointment_id)

    def delete(
        self,
        appointment_id: int
    ):

        self.execute("""
            DELETE FROM appointment
            WHERE appointment_id = ?
        """, (appointment_id,))

    def search(
        self,
        keyword: str
    ) -> list[Appointment]:

        keyword = f"%{keyword}%"

        rows = self.fetch_all("""
            SELECT *
            FROM appointment
            WHERE
                appointment_code LIKE ?
                OR purpose LIKE ?
                OR clinic_name LIKE ?
                OR status LIKE ?
            ORDER BY appt_date DESC, appt_time DESC
        """, (
            keyword,
            keyword,
            keyword,
            keyword
        ))

        return [self._map_row(row) for row in rows]

    @staticmethod
    def _map_row(row) -> Appointment:

        return Appointment(
            appointment_id=row["appointment_id"],
            appointment_code=row["appointment_code"],
            appt_date=row["appt_date"],
            appt_time=row["appt_time"],
            purpose=row["purpose"],
            clinic_name=row["clinic_name"],
            status=row["status"],
            patient_id=row["patient_id"]
        )
