import uuid
from datetime import datetime

from pydantic import BaseModel


class ClaimOut(BaseModel):
    model_config = {"from_attributes": True}

    claim_id: uuid.UUID
    claim_number: str
    encounter_id: uuid.UUID
    patient_id: uuid.UUID
    payer_name: str | None
    member_id: str | None
    claim_status: str
    service_date: str
    billed_amount: float | None
    allowed_amount: float | None
    paid_amount: float | None
    patient_responsibility: float | None
    icd10_primary: str | None
    icd10_codes: str | None
    cpt_codes: str | None
    place_of_service_code: str | None
    denial_reason: str | None
    adjudication_date: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime


class ClaimCreate(BaseModel):
    payer_name: str | None = None
    member_id: str | None = None
    claim_status: str = "draft"
    service_date: str
    billed_amount: float | None = None
    allowed_amount: float | None = None
    paid_amount: float | None = None
    patient_responsibility: float | None = None
    icd10_primary: str | None = None
    icd10_codes: str | None = None
    cpt_codes: str | None = None
    place_of_service_code: str | None = None
    denial_reason: str | None = None
    adjudication_date: str | None = None
    notes: str | None = None


class ClaimUpdate(BaseModel):
    payer_name: str | None = None
    member_id: str | None = None
    claim_status: str | None = None
    billed_amount: float | None = None
    allowed_amount: float | None = None
    paid_amount: float | None = None
    patient_responsibility: float | None = None
    icd10_primary: str | None = None
    icd10_codes: str | None = None
    cpt_codes: str | None = None
    place_of_service_code: str | None = None
    denial_reason: str | None = None
    adjudication_date: str | None = None
    notes: str | None = None
