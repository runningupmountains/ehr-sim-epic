import uuid
from datetime import datetime

from pydantic import BaseModel

from app.schemas.provider import ProviderOut


class EncounterOut(BaseModel):
    model_config = {"from_attributes": True}

    encounter_id: uuid.UUID
    external_csn: str
    patient_id: uuid.UUID
    provider_id: uuid.UUID | None
    encounter_date: str
    encounter_type: str
    visit_type: str | None
    department: str | None
    facility_name: str | None
    reason_for_visit: str | None
    status: str
    created_at: datetime


class EncounterWithProviderOut(EncounterOut):
    provider: ProviderOut | None
