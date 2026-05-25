import typer
from services.patient_service import PatientService

patient_app = typer.Typer()
service = PatientService()

@patient_app.command()
def register(
    first_name: str,
    last_name: str,
    birthdate: str,
    sex: str
):
    """
    Register a patient.
    """

    patient = service.register_patient(
        first_name=first_name,
        last_name=last_name,
        birthdate=birthdate,
        sex=sex
    )

    typer.echo(
        f"Patient registered successfully.\n"
        f"Code: {patient.patient_code}\n"
        f"ID: {patient.patient_id}"
    )

@patient_app.command()
def list():
    """
    List all patients.
    """

    patients = service.get_all_patients()

    if not patients:
        typer.echo("No patients found.")
        return

    typer.echo("\nPatients:\n")

    for patient in patients:
        typer.echo(
            f"{patient.patient_code} | "
            f"{patient.first_name} {patient.last_name} | "
            f"{patient.birthdate} | "
            f"{patient.sex}"
        )

@patient_app.command()
def get(code: str):
    """
    Get patient by code (P001).
    """

    patients = service.search_patients(code)

    if not patients:
        typer.echo("Patient not found.")
        return

    patient = patients[0]

    typer.echo(
        f"{patient.patient_code} | "
        f"{patient.first_name} {patient.last_name} | "
        f"{patient.birthdate} | "
        f"{patient.sex}"
    )

@patient_app.command()
def update(
    code: str,
    first_name: str,
    last_name: str,
    birthdate: str,
    sex: str
):
    """
    Update a patient by code (P001).
    """

    patient = service.get_patient_by_code(code)

    if not patient:
        typer.echo("Patient not found.")
        return

    service.update_patient(
        patient_id=patient.patient_id,
        first_name=first_name,
        last_name=last_name,
        birthdate=birthdate,
        sex=sex
    )

    typer.echo(f"Patient {code} updated successfully.")

@patient_app.command()
def delete(
    code: str
    ):

    patient = service.get_patient_by_code(code)

    if not patient:
        typer.echo("Patient not found.")
        return

    service.delete_patient(patient.patient_id)

    typer.echo(f"Patient {code} deleted successfully.")
