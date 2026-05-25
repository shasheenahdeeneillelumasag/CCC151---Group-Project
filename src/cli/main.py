import typer
from cli.patient_commands import patient_app
from cli.visit_record_commands import visit_record_app
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

if __name__ == "__main__":
    init_db()
    app()
