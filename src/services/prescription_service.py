from repositories.prescription_repository import PrescriptionRepository
from models.prescription import Prescription
from PyQt6.QtCore import QObject, pyqtSignal


class PrescriptionService(QObject):
    changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.repo = PrescriptionRepository()

    def get_prescription_by_code(
        self,
        code: str
    ) -> Prescription | None:

        return self.repo.get_by_code(code)

    def create_prescription(
        self,
        medication_name: str,
        dosage: str,
        prescribed_date: str,
        prescribed_by: str,
        record_id: int
    ) -> Prescription:

        prescription = Prescription(
            prescription_id=None,
            prescription_code=None,
            medication_name=medication_name,
            dosage=dosage,
            prescribed_date=prescribed_date,
            prescribed_by=prescribed_by,
            record_id=record_id
        )

        self.repo.create(prescription)
        self.changed.emit()
        return prescription

    def get_prescription_by_id(
        self,
        prescription_id: int
    ) -> Prescription | None:

        return self.repo.get_by_id(prescription_id)

    def get_all_prescriptions(self) -> list[Prescription]:

        return self.repo.get_all()

    def get_prescriptions_by_record_id(
        self,
        record_id: int
    ) -> list[Prescription]:

        return self.repo.get_by_record_id(record_id)

    def search_prescriptions(
        self,
        keyword: str
    ) -> list[Prescription]:

        return self.repo.search(keyword)

    def update_prescription(
        self,
        prescription_id: int,
        medication_name: str,
        dosage: str,
        prescribed_date: str,
        prescribed_by: str,
        record_id: int
    ):

        prescription = Prescription(
            prescription_id=prescription_id,
            prescription_code=None,  # ignored on update
            medication_name=medication_name,
            dosage=dosage,
            prescribed_date=prescribed_date,
            prescribed_by=prescribed_by,
            record_id=record_id
        )

        self.repo.update(prescription)
        self.changed.emit()
        return prescription

    def delete_prescription(
        self,
        prescription_id: int
    ):

        self.repo.delete(prescription_id)
        self.changed.emit()
