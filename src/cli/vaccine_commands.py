import typer
from services.vaccine_service import VaccinationService
from models.vaccination_shot import VaccinationShot
from datetime import datetime

vaccine_app = typer.Typer()

service = VaccinationService()

@vaccine_app.command()
def create(
    vaccine_id: str,
    vaccination_name: str,
    date_administered: str,
    facility: str,
    dose_number: int,
    schedule_date: str,
    patient_id: str
):
    vaccine = VaccinationShot(
        vaccine_id=vaccine_id,
        vaccination_name=vaccination_name,
        date_administered=datetime.strptime(date_administered, "%Y-%m-%d").date(),
        facility=facility,
        dose_number=dose_number,
        schedule_date=datetime.strptime(schedule_date, "%Y-%m-%d").date(),
        status="Pending",
        patient_id=patient_id
        )


    try:

        service.add_vaccination(
            vaccine
        )

        typer.echo(
            "Vaccine Created"
        )

    except ValueError as e:

        typer.echo(
            f"Error: {e}"
        )

@vaccine_app.command()
def list(
    patient_id: str
):

    vaccines = (
        service.get_patient_vaccinations(
            patient_id
        )
    )

    if not vaccines:

        typer.echo(
            "No vaccinations found."
        )

        raise typer.Exit()

    for vac in vaccines:

        typer.echo(
            f"{vac.vaccination_name} | "
            f"Dose {vac.dose_number} | "
            f"{vac.schedule_date} | "
            f"{vac.status}"
        )
