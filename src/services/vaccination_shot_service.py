from repositories.vaccination_shot_repository import (
    VaccinationShotRepository
)
from models.vaccination_shot import VaccinationShot
from PyQt6.QtCore import QObject, pyqtSignal



class VaccinationShotService(QObject):
    changed = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.repo = VaccinationShotRepository()

    def get_vaccination_by_code(
        self,
        code: str
    ) -> VaccinationShot | None:

        return self.repo.get_by_code(code)

    def create_vaccination(
        self,
        vaccination_name: str,
        date_administered: str,
        facility: str,
        dose_number: int,
        schedule_date: str | None,
        status: str,
        patient_id: int
    ) -> VaccinationShot:

        vaccination = VaccinationShot(
            vaccine_id=None,
            vaccine_code=None,
            vaccination_name=vaccination_name,
            date_administered=date_administered,
            facility=facility,
            dose_number=dose_number,
            schedule_date=schedule_date,
            status=status,
            patient_id=patient_id
        )

        self.repo.create(vaccination)
        self.changed.emit()
        return vaccination

    def get_vaccination_by_id(
        self,
        vaccine_id: int
    ) -> VaccinationShot | None:

        return self.repo.get_by_id(vaccine_id)

    def get_all_vaccinations(
        self
    ) -> list[VaccinationShot]:

        return self.repo.get_all()

    def get_vaccinations_by_patient_id(
        self,
        patient_id: int
    ) -> list[VaccinationShot]:

        return self.repo.get_by_patient_id(patient_id)

    def search_vaccinations(
        self,
        keyword: str
    ) -> list[VaccinationShot]:

        return self.repo.search(keyword)

    def update_vaccination(
        self,
        vaccine_id: int,
        vaccination_name: str,
        date_administered: str,
        facility: str,
        dose_number: int,
        schedule_date: str | None,
        status: str,
        patient_id: int
    ) -> VaccinationShot:

        vaccination = VaccinationShot(
            vaccine_id=vaccine_id,
            vaccine_code=None,
            vaccination_name=vaccination_name,
            date_administered=date_administered,
            facility=facility,
            dose_number=dose_number,
            schedule_date=schedule_date,
            status=status,
            patient_id=patient_id
        )

        self.repo.update(vaccination)
        self.changed.emit()
        return vaccination

    def delete_vaccination(
        self,
        vaccine_id: int
    ):

        self.repo.delete(vaccine_id)
        self.changed.emit()
