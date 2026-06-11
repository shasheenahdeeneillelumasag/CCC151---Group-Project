import typer
from services.vaccination_shot_service import VaccinationShotService
from services.patient_service import PatientService

vaccine_shot_app = typer.Typer()
service = VaccinationShotService()
patient_service = PatientService()

@vaccine_shot_app.command()
def list():
    """
    List all vaccine shots.
    """

    vaccines = service.get_all_vaccinations()

    if not vaccines:
        typer.echo("No diagnoses found.")
        return

    typer.echo("\nVaccines:\n")

    for vaccine in vaccines:

        patient = patient_service.get_patient_by_id(vaccine.patient_id)

        typer.echo(
            f"{vaccine.vaccine_code} | "
            f"{vaccine.date_administered if vaccine.date_administered else "Not Administered"} | "
            f"{vaccine.schedule_date if vaccine.schedule_date else "No Schedule"} | "
            f"{vaccine.dose_number} | "
            f"Visit: {patient.patient_code if patient else 'Unknown'}"
        )
