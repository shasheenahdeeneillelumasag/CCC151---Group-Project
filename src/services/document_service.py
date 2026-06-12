from datetime import date

from models.document import Document
from repositories.document_repository import DocumentRepository
from PyQt6.QtCore import QObject, pyqtSignal

class DocumentService(QObject):
    changed = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.repo = DocumentRepository()


    def _create_document(
        self,
        doc_filename: str,
        date_uploaded: date,
        *,
        vaccine_id: int | None = None,
        record_id: int | None = None,
        diagnosis_id: int | None = None,
        prescription_id: int | None = None
    ) -> Document:

        document = Document(
            doc_id=None,
            doc_code=None,
            doc_filename=doc_filename,
            date_uploaded=date_uploaded,
            vaccine_id=vaccine_id,
            record_id=record_id,
            diagnosis_id=diagnosis_id,
            prescription_id=prescription_id
        )

        self.repo.create(document)
        self.changed.emit()
        return document

    def create_vaccine_document(
        self,
        doc_filename: str,
        date_uploaded: date,
        vaccine_id: int
    ) -> Document:

        return self._create_document(
            doc_filename=doc_filename,
            date_uploaded=date_uploaded,
            vaccine_id=vaccine_id
        )

    def create_record_document(
        self,
        doc_filename: str,
        date_uploaded: date,
        record_id: int
    ) -> Document:

        return self._create_document(
            doc_filename=doc_filename,
            date_uploaded=date_uploaded,
            record_id=record_id
        )

    def create_diagnosis_document(
        self,
        doc_filename: str,
        date_uploaded: date,
        diagnosis_id: int
    ) -> Document:

        return self._create_document(
            doc_filename=doc_filename,
            date_uploaded=date_uploaded,
            diagnosis_id=diagnosis_id
        )

    def create_prescription_document(
        self,
        doc_filename: str,
        date_uploaded: date,
        prescription_id: int
    ) -> Document:

        return self._create_document(
            doc_filename=doc_filename,
            date_uploaded=date_uploaded,
            prescription_id=prescription_id
        )


    def get_document_by_id(
        self,
        doc_id: int
    ) -> Document | None:

        return self.repo.get_by_id(doc_id)

    def get_document_by_code(
        self,
        doc_code: str
    ) -> Document | None:

        return self.repo.get_by_code(doc_code)

    def get_all_documents(self) -> list[Document]:

        return self.repo.get_all()

    def search_documents(
        self,
        keyword: str
    ) -> list[Document]:

        return self.repo.search(keyword)

    def get_documents_by_vaccine_id(
        self,
        vaccine_id: int
    ) -> list[Document]:

        return self.repo.get_by_vaccine_id(vaccine_id)

    def get_documents_by_record_id(
        self,
        record_id: int
    ) -> list[Document]:

        return self.repo.get_by_record_id(record_id)

    def get_documents_by_diagnosis_id(
        self,
        diagnosis_id: int
    ) -> list[Document]:

        return self.repo.get_by_diagnosis_id(diagnosis_id)

    def get_documents_by_prescription_id(
        self,
        prescription_id: int
    ) -> list[Document]:

        return self.repo.get_by_prescription_id(prescription_id)


    def update_document(
        self,
        doc_id: int,
        doc_filename: str,
        date_uploaded: date,
        vaccine_id: int | None = None,
        record_id: int | None = None,
        diagnosis_id: int | None = None,
        prescription_id: int | None = None
    ) -> Document:

        document = Document(
            doc_id=doc_id,
            doc_code=None,
            doc_filename=doc_filename,
            date_uploaded=date_uploaded,
            vaccine_id=vaccine_id,
            record_id=record_id,
            diagnosis_id=diagnosis_id,
            prescription_id=prescription_id
        )

        self.repo.update(document)
        self.changed.emit()
        return document



    def delete_document(
        self,
        doc_id: int
    ):

        self.repo.delete(doc_id)
        self.changed.emit()
