from database.connection import get_connection


class BaseRepository:

    def execute(
        self,
        query: str,
        params: tuple = ()
    ):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()

    def fetch_one(
        self,
        query: str,
        params: tuple = ()
    ):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)

            return cursor.fetchone()

    def fetch_all(
        self,
        query: str,
        params: tuple = ()
    ):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)

            return cursor.fetchall()
