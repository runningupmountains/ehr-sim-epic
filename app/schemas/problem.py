import uuid
from datetime import datetime

from pydantic import BaseModel


class ProblemOut(BaseModel):
    model_config = {"from_attributes": True}

    problem_id: uuid.UUID
    patient_id: uuid.UUID
    diagnosis_name: str
    icd10_code: str | None
    status: str
    onset_date: str | None
    created_at: datetime
