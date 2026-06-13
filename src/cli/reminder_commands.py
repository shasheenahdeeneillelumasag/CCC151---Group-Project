import typer

from services.container import reminder_service, patient_service, appointment_service, vaccination_shot_service
from models.reminder import Reminder

reminder_app = typer.Typer()
service = reminder_service

@reminder_app.command()
def list_by_patient(patient_code: str):
    """
    List Reminders by patient.
    """

    reminders = service.get_active_patient_reminders(patient_service.get_patient_by_code(patient_code).patient_id)

    if not reminders:
        typer.echo("no reminders found")
        return

    typer.echo("Reminders:")

    for reminder in reminders:
        source_code = None

        if reminder.source_type == "appointment":
            source_code = appointment_service.get_appointment_by_id(reminder.source_id).appointment_code
        else:
            source_code = vaccination_shot_service.get_vaccination_by_id(reminder.source_id).vaccine_code

        typer.echo(
            f"{reminder.source_type} | "
            f"{source_code} | "
            f"{reminder.schedule_date} |"
            f"{reminder.status} |"
            f"{reminder.title} |"
            f"{reminder.subtitle}"
        )
    
