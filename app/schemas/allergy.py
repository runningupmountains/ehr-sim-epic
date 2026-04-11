import uuid
from datetime import datetime

from pydantic import BaseModel


class AllergyOut(BaseModel):
    model_config = {"from_attributes": True}

    allergy_id: uuid.UUID
    patient_id: uuid.UUID
    allergen: str
    reaction: str | None
    severity: str | None
    status: str
    created_at: datetime
