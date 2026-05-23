import typer
from cli.patient_commands import patient_app
from cli.appointment_commands import appointment_app
from database.init_db import init_db

app = typer.Typer()

app.add_typer(
    patient_app,
    name="patient"
)

app.add_typer(
    appointment_app,
    name="appointment"
)



if __name__ == "__main__":
    init_db()
    app()
