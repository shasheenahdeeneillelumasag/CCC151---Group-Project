from dataclasses import dataclass
from datetime import date


@dataclass
class Document:
    doc_id: int
    doc_code: str

    doc_filename: str
    date_uploaded: date
    diagnosis_id: int | None
    vaccine_id: int | None
    record_id: int | None
    prescription_id: int | None
