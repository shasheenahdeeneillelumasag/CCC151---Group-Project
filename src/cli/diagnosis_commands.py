import typer
from services.diagnosis_service import DiagnosisService
from services.visit_record_service import VisitRecordService

service = DiagnosisService()
visit_record_service = VisitRecordService()
diagnosis_app = typer.Typer()

@diagnosis_app.command()
def register(
    record_code: str,
    diagnosis_name: str,
    description: str,
    ):
    """
    Register a diagnosis.
    """

    visit = visit_record_service.get_record_by_code(record_code)

    diagnosis = service.create_diagnosis(
        diagnosis_name=diagnosis_name,
        description=description,
        diagnosed_date= visit.visit_date,
        record_id= visit.record_id
            )

    typer.echo(
        f"Diagnosis registered successfully.\n"
        f"Code: {diagnosis.diagnosis_code}\n"
        f"ID: {diagnosis.diagnosis_id}"
    )

@diagnosis_app.command()
def list():
    """
    List all diagnoses.
    """

    diagnoses = service.get_all_diagnoses()

    if not diagnoses:
        typer.echo("No diagnoses found.")
        return

    typer.echo("\nDiagnoses:\n")

    for diagnosis in diagnoses:

        visit = visit_record_service.get_visit_record_by_id(diagnosis.record_id)

        typer.echo(
            f"{diagnosis.diagnosis_code} | "
            f"{diagnosis.diagnosed_date} | "
            f"{diagnosis.diagnosis_name} | "
            f"{diagnosis.description} | "
            f"Visit: {visit.record_code if visit else 'Unknown'}"
        )

@diagnosis_app.command()
def delete(
    code: str
    ):

    diagnosis = service.get_diagnosis_by_code(code)

    if not diagnosis:
        typer.echo("Diagnosis Not Found")
        return

    service.delete_diagnosis(diagnosis.diagnosis_id)

    typer.echo(f"Diagnosis {code} deleted successfully.")
