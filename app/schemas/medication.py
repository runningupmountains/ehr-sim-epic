import uuid
from datetime import datetime

from pydantic import BaseModel


class MedicationOut(BaseModel):
    model_config = {"from_attributes": True}

    medication_id: uuid.UUID
    patient_id: uuid.UUID
    medication_name: str
    sig: str | None
    status: str
    start_date: str | None
    end_date: str | None
    created_at: datetime
