import uuid
from datetime import datetime

from pydantic import BaseModel


class VitalSignsOut(BaseModel):
    model_config = {"from_attributes": True}

    vital_id: uuid.UUID
    encounter_id: uuid.UUID
    patient_id: uuid.UUID
    height_cm: float | None
    weight_kg: float | None
    bmi: float | None
    systolic_bp: int | None
    diastolic_bp: int | None
    pulse: int | None
    temperature_f: float | None
    spo2: int | None
    recorded_at: str | None
    created_at: datetime
