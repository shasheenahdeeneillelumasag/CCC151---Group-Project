from services.visit_record_service import VisitRecordService
from services.diagnosis_service import DiagnosisService
from services.prescription_service import PrescriptionService


from models.medical_history_item import (
    MedicalHistoryItem
)


class MedicalHistoryService:

    def __init__(self, visit_record_service, diagnosis_service, prescription_service):

        self.record_service = visit_record_service

        self.diagnosis_service = diagnosis_service

        self.prescription_service = prescription_service

    def get_patient_history(
        self,
        patient_id: int
    ) -> list[MedicalHistoryItem]:

        history = []

        records = (
            self.record_service
            .get_visit_records_by_patient_id(
                patient_id
            )
        )

        for record in records:

            diagnoses = (
                self.diagnosis_service
                .get_diagnoses_by_record_id(
                    record.record_id
                )
            )

            prescriptions = (
                self.prescription_service
                .get_prescriptions_by_record_id(
                    record.record_id
                )
            )

            history.append(
                MedicalHistoryItem(
                    record=record,
                    diagnoses=diagnoses,
                    prescriptions=prescriptions
                )
            )

        return history
