import typer

from services.visit_record_service import VisitRecordService
from services.patient_service import PatientService


visit_record_app = typer.Typer()

service = VisitRecordService()
patient_service = PatientService()


@visit_record_app.command()
def register(
    patient_code: str,
    visit_date: str,
    weight_kg: float = None,
    blood_pressure: str = None
):
    """
    Register a visit record.
    """

    patient = patient_service.get_patient_by_code(patient_code)

    if not patient:
        typer.echo("Patient not found.")
        return

    visit_record = service.create_visit_record(
        visit_date=visit_date,
        weight_kg=weight_kg,
        blood_pressure=blood_pressure,
        patient_id=patient.patient_id
    )

    typer.echo(
        f"Visit record registered successfully.\n"
        f"Code: {visit_record.record_code}\n"
        f"ID: {visit_record.record_id}"
    )


@visit_record_app.command()
def list():
    """
    List all visit records.
    """

    records = service.get_all_visit_records()

    if not records:
        typer.echo("No visit records found.")
        return

    typer.echo("\nVisit Records:\n")

    for record in records:

        patient = patient_service.get_patient_by_id(record.patient_id)

        typer.echo(
            f"{record.record_code} | "
            f"{record.visit_date} | "
            f"{record.weight_kg} kg | "
            f"{record.blood_pressure} | "
            f"Patient: {patient.patient_code if patient else 'Unknown'}"
        )


@visit_record_app.command()
def get(code: str):
    """
    Get visit record by code (R001).
    """

    record = service.get_record_by_code(code)

    if not record:
        typer.echo("Visit record not found.")
        return

    patient = patient_service.get_patient_by_id(record.patient_id)

    typer.echo(
        f"{record.record_code} | "
        f"{record.visit_date} | "
        f"{record.weight_kg} kg | "
        f"{record.blood_pressure} | "
        f"Patient: {patient.patient_code if patient else 'Unknown'}"
    )


@visit_record_app.command()
def list_by_patient(patient_code: str):
    """
    List visit records for a patient.
    """

    patient = patient_service.get_patient_by_code(patient_code)

    if not patient:
        typer.echo("Patient not found.")
        return

    records = service.get_visit_records_by_patient_id(patient.patient_id)

    if not records:
        typer.echo("No visit records found.")
        return

    typer.echo(f"\nVisit Records for {patient.patient_code}:\n")

    for record in records:
        typer.echo(
            f"{record.record_code} | "
            f"{record.visit_date} | "
            f"{record.weight_kg} kg | "
            f"{record.blood_pressure}"
        )


@visit_record_app.command()
def update(
    code: str,
    visit_date: str,
    weight_kg: float = None,
    blood_pressure: str = None
):
    """
    Update a visit record by code (R001).
    """

    record = service.get_record_by_code(code)

    if not record:
        typer.echo("Visit record not found.")
        return

    service.update_visit_record(
        record_id=record.record_id,
        visit_date=visit_date,
        weight_kg=weight_kg,
        blood_pressure=blood_pressure,
        patient_id=record.patient_id
    )

    typer.echo(f"Visit record {code} updated successfully.")


@visit_record_app.command()
def delete(code: str):
    """
    Delete a visit record by code (R001).
    """

    record = service.get_record_by_code(code)

    if not record:
        typer.echo("Visit record not found.")
        return

    service.delete_visit_record(record.record_id)

    typer.echo(f"Visit record {code} deleted successfully.")
