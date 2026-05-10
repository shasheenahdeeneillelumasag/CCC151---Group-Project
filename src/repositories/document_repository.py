from models.document import Document
from repositories.base_repository import BaseRepository


class DocumentRepository(BaseRepository):

    def create(self, document: Document):

        self.execute("""
            INSERT INTO document (
                doc_id,
                doc_filename,
                date_uploaded,
                vaccine_id,
                record_id
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            document.doc_id,
            document.doc_filename,
            document.date_uploaded,
            document.vaccine_id,
            document.record_id
        ))

    def get_by_vaccine(
        self,
        vaccine_id: str
    ) -> list[Document]:

        rows = self.fetch_all("""
            SELECT *
            FROM document
            WHERE vaccine_id = ?
        """, (vaccine_id,))

        return [
            Document(**row)
            for row in rows
        ]

    def get_by_record(
        self,
        record_id: str
    ) -> list[Document]:

        rows = self.fetch_all("""
            SELECT *
            FROM document
            WHERE record_id = ?
        """, (record_id,))

        return [
            Document(**row)
            for row in rows
        ]

    def delete(self, doc_id: str):

        self.execute("""
            DELETE FROM document
            WHERE doc_id = ?
        """, (doc_id,))
