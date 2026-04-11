import uuid

from pydantic import BaseModel


class ProviderOut(BaseModel):
    model_config = {"from_attributes": True}

    provider_id: uuid.UUID
    npi: str
    first_name: str
    last_name: str
    specialty: str | None
    department: str | None
    phone: str | None
    email: str | None

    @property
    def full_name(self) -> str:
        return f"Dr. {self.first_name} {self.last_name}"
