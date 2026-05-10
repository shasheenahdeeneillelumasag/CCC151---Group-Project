from repositories.patient_repository import PatientRepository
from models.patient import Patient

class PatientService:

    def __init__(self):
        self.repo = PatientRepository()

    def register_patient(
        self,
        patient_id,
        first_name,
        last_name,
        birthdate,
        sex
    ):

        patient = Patient(
            patient_id=patient_id,
            first_name=first_name,
            last_name=last_name,
            birthdate=birthdate,
            sex=sex
        )

        self.repo.create(patient)

    def get_all_patients(self):
        return self.repo.get_all()
