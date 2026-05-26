import typer
from services.patient_contact_service import PatientContactService
from services.patient_service import PatientService

patient_contact_app = typer.Typer()
service = PatientContactService()
patient_service = PatientService()

@patient_contact_app.command()
def register(patient_code: str, contact_number: str):
    """

    """

    patient = patient_service.get_patient_by_code(patient_code)

    if not patient:
        typer.echo("Patient not found.")
        return

    contact = service.add_contact(patient_code, contact_number)

    typer.echo(
        f"Contact registered successfully.\n"
        f"Code: {patient.patient_code}\n"
        f"Number: {contact.contact_number}"
    )

@patient_contact_app.command()
def list_by_patient(patient_code: str):
    """
    List contact numbers of a patient.
    """

    patient = patient_service.get_patient_by_code(
        patient_code
    )

    if not patient:
        typer.echo("Patient not found.")
        return

    records = service.get_contacts_by_patient_code(
        patient_code
    )

    if not records:
        typer.echo("No Contacts found.")
        return

    typer.echo(
        f"\nContact Numbers for {patient.patient_code}:\n"
    )

    for record in records:
        typer.echo(
            f"{record.contact_id} | "
            f"{record.contact_number}"
        )
