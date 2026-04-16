import uuid
from datetime import datetime

from pydantic import BaseModel, computed_field

from app.schemas.provider import ProviderOut

# CMS Place of Service codes derived from encounter_type
_POS_MAP: dict[str, str] = {
    "office visit":   "11",
    "telehealth":     "02",
    "inpatient":      "21",
    "emergency":      "23",
    "outpatient":     "22",
    "urgent care":    "20",
    "home health":    "12",
    "skilled nursing":"31",
}


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

    @computed_field
    @property
    def place_of_service_code(self) -> str | None:
        return _POS_MAP.get(self.encounter_type.lower().strip())


class EncounterWithProviderOut(EncounterOut):
    provider: ProviderOut | None
