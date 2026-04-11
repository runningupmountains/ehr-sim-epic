import uuid
from datetime import datetime

from sqlalchemy import UUID, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Encounter(Base):
    __tablename__ = "encounters"

    encounter_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    external_csn: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("patients.patient_id"), nullable=False
    )
    provider_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("providers.provider_id"), nullable=True
    )
    encounter_date: Mapped[str] = mapped_column(String(10), nullable=False)  # YYYY-MM-DD
    encounter_type: Mapped[str] = mapped_column(String(100), nullable=False)
    visit_type: Mapped[str | None] = mapped_column(String(100))
    department: Mapped[str | None] = mapped_column(String(100))
    facility_name: Mapped[str | None] = mapped_column(String(200))
    reason_for_visit: Mapped[str | None] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="completed")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    patient: Mapped["Patient"] = relationship("Patient", back_populates="encounters")  # noqa: F821
    provider: Mapped["Provider"] = relationship("Provider", back_populates="encounters")  # noqa: F821
    clinical_notes: Mapped[list["ClinicalNote"]] = relationship(  # noqa: F821
        "ClinicalNote", back_populates="encounter"
    )
    lab_results: Mapped[list["LabResult"]] = relationship(  # noqa: F821
        "LabResult", back_populates="encounter"
    )
    vital_signs: Mapped[list["VitalSigns"]] = relationship(  # noqa: F821
        "VitalSigns", back_populates="encounter"
    )
    documents: Mapped[list["Document"]] = relationship(  # noqa: F821
        "Document", back_populates="encounter"
    )
