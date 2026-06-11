from database.connection import get_connection
from pathlib import Path

def init_db():
    schema_path = Path(__file__).resolve().parent / "schema.sql"

    with open(schema_path, "r", encoding="utf-8") as f:
        sql_script = f.read()

    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.executescript(sql_script)
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_vaccine_patient ON vaccination_shots(patient_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_appointment_patient ON appointment(patient_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_visit_patient ON visit_record(patient_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_diagnosis_record ON diagnosis(record_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_prescription_record ON prescription(record_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_document_vaccine ON document(vaccine_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_document_record ON document(record_id)")

        conn.commit()

if __name__ == "__main__":
    init_db()
    print("Database initialized.")