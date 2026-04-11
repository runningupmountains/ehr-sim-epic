import uuid

from sqlalchemy import UUID, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Provider(Base):
    __tablename__ = "providers"

    provider_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    npi: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    specialty: Mapped[str | None] = mapped_column(String(100))
    department: Mapped[str | None] = mapped_column(String(100))
    phone: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(200))

    patients: Mapped[list["Patient"]] = relationship(  # noqa: F821
        "Patient",
        back_populates="primary_provider",
        foreign_keys="Patient.primary_provider_id",
    )
    encounters: Mapped[list["Encounter"]] = relationship(  # noqa: F821
        "Encounter", back_populates="provider"
    )
