from database.connection import get_connection

class BaseRepository:

    def execute(
        self,
        query: str,
        params: tuple = ()
    ):

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(query, params)

        conn.commit()

        conn.close()

    def execute_returning_id(
        self,
        query: str,
        params: tuple = ()
    ) -> int:

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(query, params)

        last_id = cursor.lastrowid

        conn.commit()

        conn.close()

        return last_id

    def fetch_one(
        self,
        query: str,
        params: tuple = ()
    ):

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(query, params)

        row = cursor.fetchone()

        conn.close()

        return row

    def fetch_all(
        self,
        query: str,
        params: tuple = ()
    ):

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(query, params)

        rows = cursor.fetchall()

        conn.close()

        return rows
