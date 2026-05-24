from models.vaccination_shot import VaccinationShot

from repositories.patient_repository import (
    PatientRepository
)

from repositories.vaccination_repository import (
    VaccinationRepository
)


class VaccinationService:

    def __init__(self):

        self.patient_repo = (
            PatientRepository()
        )

        self.vaccine_repo = (
            VaccinationRepository()
        )

    def add_vaccination(
        self,
        vaccination: VaccinationShot
    ) -> None:

        patient = self.patient_repo.get_by_id(
            vaccination.patient_id
        )

        if not patient:
            raise ValueError(
                "Patient does not exist"
            )

        if vaccination.dose_number < 1:
            raise ValueError(
                "Dose number must be positive"
            )

        self.vaccine_repo.create(
            vaccination
        )

    def complete_vaccination(
        self,
        vaccine_id: str
    ) -> None:

        vaccine = (
            self.vaccine_repo.get_by_id(
                vaccine_id
            )
        )

        if not vaccine:
            raise ValueError(
                "Vaccination not found"
            )

        if vaccine.status == "Completed":
            return

        self.vaccine_repo.update_status(
            vaccine_id,
            "Completed"
        )

    def get_patient_vaccinations(
        self,
        patient_id: str
    ) -> list[VaccinationShot]:

        return (
            self.vaccine_repo
            .get_by_patient(patient_id)
        )

    def get_pending_vaccinations(
        self
    ) -> list[VaccinationShot]:

        return (
            self.vaccine_repo
            .get_by_status("Pending")
        )

    def get_overdue_vaccinations(
        self
    ) -> list[VaccinationShot]:

        return (
            self.vaccine_repo
            .get_overdue()
        )

    def get_patient_vaccinations(
        self,
        patient_id: str
    ):

        return (
            self.vaccine_repo
            .get_by_patient(patient_id)
        )
