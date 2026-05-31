from dataclasses import dataclass

from models.visit_record import VisitRecord
from models.diagnosis import Diagnosis
from models.prescription import Prescription

@dataclass
class MedicalHistoryItem:
    record: VisitRecord
    diagnoses: list[Diagnosis]
    prescriptions: list[Prescription]
