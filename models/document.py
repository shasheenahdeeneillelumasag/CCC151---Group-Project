from dataclasses import dataclass
from datetime import date


@dataclass
class Document:
    doc_id: str
    doc_filename: str
    date_uploaded: date
    vaccine_id: str | None
    record_id: str | None
