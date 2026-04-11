import uuid
from datetime import datetime

from pydantic import BaseModel


class DocumentOut(BaseModel):
    model_config = {"from_attributes": True}

    document_id: uuid.UUID
    patient_id: uuid.UUID
    encounter_id: uuid.UUID | None
    document_type: str
    title: str
    storage_key: str | None
    created_at: datetime
