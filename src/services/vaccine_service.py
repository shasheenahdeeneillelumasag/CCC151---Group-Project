from datetime import date

from models.vaccination_shot import (
    VaccinationShot
)

from repositories.patient_repository import (
    PatientRepository
)

from repositories.vaccination_repository import (
    VaccinationRepository
)


class VaccinationService:

    def __init__(self):

        self.patient_repo = PatientRepository()

        self.vaccine_repo = (
            VaccinationRepository()
        )

    def add_vaccination(
        self,
        vaccination: VaccinationShot
    ):

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

    def mark_completed(
        self,
        vaccine_id: str
    ):

        vaccine = (
            self.vaccine_repo.get_by_id(
                vaccine_id
            )
        )

        if not vaccine:

            raise ValueError(
                "Vaccination not found"
            )

        vaccine.status = "Completed"

        self.vaccine_repo.update(
            vaccine
        )

    def get_pending_vaccines(self):

        return (
            self.vaccine_repo
            .get_by_status("Pending")
        )

    def get_overdue_vaccines(self):

        vaccines = (
            self.vaccine_repo
            .get_by_status("Pending")
        )

        overdue = []

        for vaccine in vaccines:

            if vaccine.schedule_date < date.today():

                overdue.append(vaccine)

        return overdue
