import typer
from cli.patient_commands import patient_app
from database.init_db import init_db

app = typer.Typer()

app.add_typer(
    patient_app,
    name="patient"
)


if __name__ == "__main__":
    init_db()
    app()
