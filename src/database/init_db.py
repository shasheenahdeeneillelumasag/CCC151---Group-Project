from database.connection import get_connection


def init_db():
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patient (
                patient_id TEXT PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                birthdate TEXT NOT NULL,
                sex TEXT NOT NULL
            )
        """)

        conn.commit()


if __name__ == "__main__":
    init_db()
    print("Database initialized.")
