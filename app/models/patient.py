import uuid
from datetime import datetime

from sqlalchemy import UUID, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Patient(Base):
    __tablename__ = "patients"

    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    external_mrn: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    dob: Mapped[str] = mapped_column(String(10), nullable=False)  # YYYY-MM-DD
    sex: Mapped[str] = mapped_column(String(10), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(200))
    address_line1: Mapped[str | None] = mapped_column(String(200))
    city: Mapped[str | None] = mapped_column(String(100))
    state: Mapped[str | None] = mapped_column(String(2))
    zip_code: Mapped[str | None] = mapped_column(String(10))
    primary_provider_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("providers.provider_id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    primary_provider: Mapped["Provider"] = relationship(  # noqa: F821
        "Provider", back_populates="patients", foreign_keys=[primary_provider_id]
    )
    encounters: Mapped[list["Encounter"]] = relationship(  # noqa: F821
        "Encounter", back_populates="patient"
    )
    medications: Mapped[list["Medication"]] = relationship(  # noqa: F821
        "Medication", back_populates="patient"
    )
    allergies: Mapped[list["Allergy"]] = relationship(  # noqa: F821
        "Allergy", back_populates="patient"
    )
    problems: Mapped[list["Problem"]] = relationship(  # noqa: F821
        "Problem", back_populates="patient"
    )
    lab_results: Mapped[list["LabResult"]] = relationship(  # noqa: F821
        "LabResult", back_populates="patient"
    )
    documents: Mapped[list["Document"]] = relationship(  # noqa: F821
        "Document", back_populates="patient"
    )
