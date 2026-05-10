from datetime import date

from models.appointment import Appointment

from repositories.patient_repository import (
    PatientRepository
)

from repositories.appointment_repository import (
    AppointmentRepository
)


class AppointmentService:

    def __init__(self):

        self.patient_repo = PatientRepository()

        self.appointment_repo = (
            AppointmentRepository()
        )

    def create_appointment(
        self,
        appointment: Appointment
    ):

        patient = self.patient_repo.get_by_id(
            appointment.patient_id
        )

        if not patient:

            raise ValueError(
                "Patient does not exist"
            )

        if appointment.appt_date < date.today():

            raise ValueError(
                "Appointment cannot be in the past"
            )

        self.appointment_repo.create(
            appointment
        )

    def complete_appointment(
        self,
        appointment_id: str
    ):

        appointment = (
            self.appointment_repo.get_by_id(
                appointment_id
            )
        )

        if not appointment:

            raise ValueError(
                "Appointment not found"
            )

        appointment.status = "Completed"

        self.appointment_repo.update(
            appointment
        )

    def cancel_appointment(
        self,
        appointment_id: str
    ):

        appointment = (
            self.appointment_repo.get_by_id(
                appointment_id
            )
        )

        if not appointment:

            raise ValueError(
                "Appointment not found"
            )

        appointment.status = "Cancelled"

        self.appointment_repo.update(
            appointment
        )

    def get_patient_appointments(
        self,
        patient_id: str
    ):

        return (
            self.appointment_repo
            .get_by_patient(patient_id)
        )
