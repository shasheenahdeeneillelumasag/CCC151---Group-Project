import typer

from services.patient_service import PatientService

patient_app = typer.Typer()

service = PatientService()


@patient_app.command()
def register(
    patient_id: str,
    first_name: str,
    last_name: str,
    birthdate: str,
    sex: str
):
    """
    Register a patient.
    """

    service.register_patient(
        patient_id=patient_id,
        first_name=first_name,
        last_name=last_name,
        birthdate=birthdate,
        sex=sex
    )

    typer.echo("Patient registered successfully.")


@patient_app.command()
def list():
    """
    List all patients.
    """

    patients = service.get_all_patients()

    if not patients:
        typer.echo("No patients found.")
        return

    for patient in patients:
        typer.echo(
            f"{patient.patient_id} | "
            f"{patient.first_name} {patient.last_name} | "
            f"{patient.birthdate} | "
            f"{patient.sex}"
        )
