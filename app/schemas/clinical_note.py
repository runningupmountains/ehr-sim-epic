import uuid
from datetime import datetime

from pydantic import BaseModel

from app.schemas.provider import ProviderOut


class ClinicalNoteOut(BaseModel):
    model_config = {"from_attributes": True}

    note_id: uuid.UUID
    encounter_id: uuid.UUID
    patient_id: uuid.UUID
    provider_id: uuid.UUID | None
    note_type: str
    title: str
    body_text: str
    signed_at: datetime | None
    created_at: datetime


class ClinicalNoteWithProviderOut(ClinicalNoteOut):
    provider: ProviderOut | None
