import uuid
from datetime import datetime

from pydantic import BaseModel


class LabResultOut(BaseModel):
    model_config = {"from_attributes": True}

    lab_result_id: uuid.UUID
    patient_id: uuid.UUID
    encounter_id: uuid.UUID | None
    test_name: str
    result_value: str | None
    unit: str | None
    reference_range: str | None
    abnormal_flag: str | None
    result_status: str
    ordering_provider_id: uuid.UUID | None
    collected_at: str | None
    created_at: datetime
