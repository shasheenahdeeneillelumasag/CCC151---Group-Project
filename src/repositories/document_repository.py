from repositories.base_repository import BaseRepository
from models.document import Document


class DocumentRepository(BaseRepository):

    def create(self, document: Document) -> Document:

        doc_id = self.execute_returning_id("""
            INSERT INTO document (
                doc_code,
                doc_filename,
                date_uploaded,
                vaccine_id,
                record_id,
                diagnosis_id,
                prescription_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            "",
            document.doc_filename,
            document.date_uploaded,
            document.vaccine_id,
            document.record_id,
            document.diagnosis_id,
            document.prescription_id
        ))

        doc_code = f"DOC{doc_id:03d}"

        self.execute("""
            UPDATE document
            SET doc_code = ?
            WHERE doc_id = ?
        """, (
            doc_code,
            doc_id
        ))

        document.doc_id = doc_id
        document.doc_code = doc_code

        return document

    @staticmethod
    def _map_row(row) -> Document:

        return Document(
            doc_id=row["doc_id"],
            doc_code=row["doc_code"],
            doc_filename=row["doc_filename"],
            date_uploaded=row["date_uploaded"],
            vaccine_id=row["vaccine_id"],
            record_id=row["record_id"],
            diagnosis_id=row["diagnosis_id"],
            prescription_id=row["prescription_id"]
        )

    def get_by_id(self, doc_id: int) -> Document | None:

        row = self.fetch_one("""
            SELECT *
            FROM document
            WHERE doc_id = ?
        """, (doc_id,))

        if not row:
            return None

        return self._map_row(row)

    def update(self, document: Document) -> Document:

        if document.doc_id is None:
            raise ValueError("doc_id cannot be None")

        self.execute("""
            UPDATE document
            SET
                doc_filename = ?,
                date_uploaded = ?,
                vaccine_id = ?,
                record_id = ?,
                diagnosis_id = ?,
                prescription_id = ?
            WHERE doc_id = ?
        """, (
            document.doc_filename,
            document.date_uploaded,
            document.vaccine_id,
            document.record_id,
            document.diagnosis_id,
            document.prescription_id,
            document.doc_id
        ))

        return self.get_by_id(document.doc_id)

    def get_by_code(
        self,
        doc_code: str
    ) -> Document | None:

        row = self.fetch_one("""
            SELECT *
            FROM document
            WHERE doc_code = ?
        """, (doc_code,))

        if not row:
            return None

        return self._map_row(row)

    def get_all(self) -> list[Document]:

        rows = self.fetch_all("""
            SELECT *
            FROM document
            ORDER BY date_uploaded DESC
        """)

        return [self._map_row(row) for row in rows]

    def search(
        self,
        keyword: str
    ) -> list[Document]:

        keyword = f"%{keyword}%"

        rows = self.fetch_all("""
            SELECT *
            FROM document
            WHERE
                doc_code LIKE ?
                OR doc_filename LIKE ?
            ORDER BY date_uploaded DESC
        """, (
            keyword,
            keyword
        ))

        return [self._map_row(row) for row in rows]

    def get_by_vaccine_id(
        self,
        vaccine_id: int
    ) -> list[Document]:

        rows = self.fetch_all("""
            SELECT *
            FROM document
            WHERE vaccine_id = ?
            ORDER BY date_uploaded DESC
        """, (vaccine_id,))

        return [self._map_row(row) for row in rows]

    def get_by_diagnosis_id(
        self,
        diagnosis_id: int
    ) -> list[Document]:

        rows = self.fetch_all("""
            SELECT *
            FROM document
            WHERE diagnosis_id = ?
            ORDER BY date_uploaded DESC
        """, (diagnosis_id,))

        return [self._map_row(row) for row in rows]

    def get_by_prescription_id(
        self,
        prescription_id: int
    ) -> list[Document]:

        rows = self.fetch_all("""
            SELECT *
            FROM document
            WHERE prescription_id = ?
            ORDER BY date_uploaded DESC
        """, (prescription_id,))

        return [self._map_row(row) for row in rows]

    def get_by_record_id(
        self,
        record_id: int
    ) -> list[Document]:

        rows = self.fetch_all("""
            SELECT *
            FROM document
            WHERE record_id = ?
            ORDER BY date_uploaded DESC
        """, (record_id,))


        return [self._map_row(row) for row in rows]

    def delete(
        self,
        doc_id: int
    ):

        self.execute("""
            DELETE FROM document
            WHERE doc_id = ?
        """, (doc_id,))
