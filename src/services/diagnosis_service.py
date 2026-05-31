from repositories.diagnosis_repository import DiagnosisRepository
from models.diagnosis import Diagnosis

class DiagnosisService:

    def __init__(self):
        self.repo = DiagnosisRepository()

    def get_diagnosis_by_code(
        self,
        code: str
    ) -> Diagnosis | None:

        return self.repo.get_by_code(code)

    def create_diagnosis(
        self,
        diagnosis_name: str,
        description: str | None,
        diagnosed_date: str,
        record_id: int
    ) -> Diagnosis:

        diagnosis = Diagnosis(
            diagnosis_id=None,
            diagnosis_code=None,
            diagnosis_name=diagnosis_name,
            description=description,
            diagnosed_date=diagnosed_date,
            record_id=record_id
        )

        return self.repo.create(diagnosis)

    def get_diagnosis_by_id(
        self,
        diagnosis_id: int
    ) -> Diagnosis | None:

        return self.repo.get_by_id(diagnosis_id)

    def get_all_diagnoses(self) -> list[Diagnosis]:

        return self.repo.get_all()

    def get_diagnoses_by_record_id(
        self,
        record_id: int
    ) -> list[Diagnosis]:

        return self.repo.get_by_record_id(record_id)

    def search_diagnoses(
        self,
        keyword: str
    ) -> list[Diagnosis]:

        return self.repo.search(keyword)

    def update_diagnosis(
        self,
        diagnosis_id: int,
        diagnosis_name: str,
        description: str | None,
        diagnosed_date: str,
        record_id: int
    ):

        diagnosis = Diagnosis(
            diagnosis_id=diagnosis_id,
            diagnosis_code=None,  # ignored on update
            diagnosis_name=diagnosis_name,
            description=description,
            diagnosed_date=diagnosed_date,
            record_id=record_id
        )

        return self.repo.update(diagnosis)

    def delete_diagnosis(
        self,
        diagnosis_id: int
    ):

        self.repo.delete(diagnosis_id)
