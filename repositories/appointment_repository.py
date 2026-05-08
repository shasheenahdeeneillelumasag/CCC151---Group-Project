from models.appointment import Appointment
from repositories.base_repository import BaseRepository


class AppointmentRepository(BaseRepository):

    def create(self, appointment: Appointment):

        self.execute("""
            INSERT INTO appointment (
                appointment_id,
                appt_date,
                appt_time,
                purpose,
                clinic_name,
                status,
                patient_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            appointment.appointment_id,
            appointment.appt_date,
            appointment.appt_time,
            appointment.purpose,
            appointment.clinic_name,
            appointment.status,
            appointment.patient_id
        ))

    def get_by_id(
        self,
        appointment_id: str
    ) -> Appointment | None:

        row = self.fetch_one("""
            SELECT *
            FROM appointment
            WHERE appointment_id = ?
        """, (appointment_id,))

        if row:
            return Appointment(**row)

        return None

    def get_by_patient(
        self,
        patient_id: str
    ) -> list[Appointment]:

        rows = self.fetch_all("""
            SELECT *
            FROM appointment
            WHERE patient_id = ?
            ORDER BY appt_date DESC
        """, (patient_id,))

        return [
            Appointment(**row)
            for row in rows
        ]

    def update(self, appointment: Appointment):

        self.execute("""
            UPDATE appointment
            SET
                appt_date = ?,
                appt_time = ?,
                purpose = ?,
                clinic_name = ?,
                status = ?
            WHERE appointment_id = ?
        """, (
            appointment.appt_date,
            appointment.appt_time,
            appointment.purpose,
            appointment.clinic_name,
            appointment.status,
            appointment.appointment_id
        ))

    def delete(self, appointment_id: str):

        self.execute("""
            DELETE FROM appointment
            WHERE appointment_id = ?
        """, (appointment_id,))
