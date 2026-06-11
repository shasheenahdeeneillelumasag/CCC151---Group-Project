import typer
from cli.patient_commands import patient_app
from cli.visit_record_commands import visit_record_app
from cli.patient_contact_commands import patient_contact_app
from cli.diagnosis_commands import diagnosis_app
from cli.document_commands import document_app
from cli.vaccine_commands import vaccine_shot_app


from database.init_db import init_db

app = typer.Typer()

app.add_typer(
    patient_app,
    name="patient"
)

app.add_typer(
    visit_record_app,
    name="visit"
)

app.add_typer(
    patient_contact_app,
    name="patient-contact"
)

app.add_typer(
    diagnosis_app,
    name="diagnosis"
)

app.add_typer(
    document_app,
    name="document"
)

app.add_typer(
    vaccine_shot_app,
    name="vaccine"
)

if __name__ == "__main__":
    init_db()
    app()
