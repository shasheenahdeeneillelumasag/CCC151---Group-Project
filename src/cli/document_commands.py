import typer

from models.document import Document

from models.visit_record import VisitRecord
from models.prescription import Prescription
from models.diagnosis import Diagnosis 

from services.document_service import DocumentService
from services.patient_service import PatientService

from services.visit_record_service import VisitRecordService
from services.diagnosis_service import DiagnosisService
from services.prescription_service import PrescriptionService
from services.vaccination_shot_service import VaccinationShotService

service = DocumentService()
visit_record_service = VisitRecordService()
patient_service = PatientService()
diagnosis_service = DiagnosisService()
prescription_service = PrescriptionService()
vaccination_shot_service = VaccinationShotService()

document_app = typer.Typer()

@document_app.command()
def list():
    """
    List all documents.
    """

    documents = service.get_all_documents()

    if not documents:
        typer.echo("No documents found.")
        return

    typer.echo("\nDocuments:\n")

    for document in documents:
        currentCode = ""

        if document.record_id:
            currentCode = visit_record_service.get_visit_record_by_id(document.record_id).record_code

        if document.diagnosis_id:
            currentCode = diagnosis_service.get_diagnosis_by_id(document.diagnosis_id).diagnosis_code

        if document.prescription_id:
            currentCode = prescription_service.get_prescription_by_id(document.prescription_id).prescription_code

        if document.vaccine_id:
            currentCode = vaccination_shot_service.get_vaccination_by_id(document.vaccine_id).vaccine_code

        typer.echo(
            f"{document.doc_code} | "
            f"{document.doc_filename} | "
            f"Parent Code: {currentCode}"
        )

@document_app.command()
def delete(
    code: str
    ):

    document = service.get_document_by_code(code)

    if not document:
        typer.echo("Document not found.")
        return

    service.delete_document(document.doc_id)

    typer.echo(f"Document {code} deleted successfully.")
