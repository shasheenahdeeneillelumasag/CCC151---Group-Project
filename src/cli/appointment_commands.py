import typer

from datetime import datetime

from models.appointment import Appointment
from services.appointment_service import (
    AppointmentService
)

appointment_app = typer.Typer()

service = AppointmentService()

@appointment_app.command()
def create(
    appointment_id: str,
    patient_id: str,
    appt_date: str,
    appt_time: str,
    purpose: str,
    clinic_name: str
):

    appointment = Appointment(
        appointment_id=appointment_id,
        patient_id=patient_id,
        appt_date=datetime.strptime(
            appt_date,
            "%Y-%m-%d"
        ).date(),
        appt_time=appt_time,
        purpose=purpose,
        clinic_name=clinic_name,
        status="Scheduled"
    )

    try:

        service.create_appointment(
            appointment
        )

        typer.echo(
            "Appointment created"
        )

    except ValueError as e:

        typer.echo(
            f"Error: {e}"
        )

@appointment_app.command()
def complete(
    appointment_id: str
):

    try:

        service.complete_appointment(
            appointment_id
        )

        typer.echo(
            "Appointment completed"
        )

    except ValueError as e:

        typer.echo(
            f"Error: {e}"
        )

@appointment_app.command()
def cancel(
    appointment_id: str
):

    try:

        service.cancel_appointment(
            appointment_id
        )

        typer.echo(
            f"Appointment cancelled"
        )

    except ValueError as e:

        typer.echo(
            f"Error: {e}"
        )

@appointment_app.command()
def list(
    patient_id: str
):

    appointments = (
        service.get_patient_appointments(
            patient_id
        )
    )

    for appt in appointments:

        typer.echo(
            f"{appt.appointment_id} | "
            f"{appt.appt_date} | "
            f"{appt.status}"
        )
