import uuid
from datetime import datetime

from pydantic import BaseModel

from app.schemas.provider import ProviderOut


class PatientOut(BaseModel):
    model_config = {"from_attributes": True}

    patient_id: uuid.UUID
    external_mrn: str
    first_name: str
    last_name: str
    dob: str
    sex: str
    phone: str | None
    email: str | None
    address_line1: str | None
    city: str | None
    state: str | None
    zip_code: str | None
    primary_provider_id: uuid.UUID | None
    member_id: str | None
    payer_name: str | None
    created_at: datetime


class PatientWithProviderOut(PatientOut):
    primary_provider: ProviderOut | None
