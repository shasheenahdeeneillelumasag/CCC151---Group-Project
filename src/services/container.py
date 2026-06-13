from services.appointment_service import AppointmentService
from services.diagnosis_service import DiagnosisService
from services.document_service import DocumentService
from services.patient_service import PatientService
from services.patient_contact_service import PatientContactService
from services.prescription_service import PrescriptionService
from services.vaccination_shot_service import VaccinationShotService
from services.visit_record_service import VisitRecordService


# UI SERVICES
from services.medical_history_service import MedicalHistoryService
from services.reminder_service import ReminderService



appointment_service = AppointmentService()
diagnosis_service = DiagnosisService()
document_service = DocumentService()
patient_service = PatientService()
patient_contact_service = PatientContactService()
prescription_service = PrescriptionService()
vaccination_shot_service = VaccinationShotService()
visit_record_service = VisitRecordService()

medical_history_service = MedicalHistoryService(visit_record_service, diagnosis_service, prescription_service)
reminder_service = ReminderService(appointment_service, vaccination_shot_service)

