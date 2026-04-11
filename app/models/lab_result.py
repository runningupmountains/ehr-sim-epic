import uuid
from datetime import datetime

from sqlalchemy import UUID, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class LabResult(Base):
    __tablename__ = "lab_results"

    lab_result_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("patients.patient_id"), nullable=False
    )
    encounter_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("encounters.encounter_id"), nullable=True
    )
    test_name: Mapped[str] = mapped_column(String(200), nullable=False)
    result_value: Mapped[str | None] = mapped_column(String(100))
    unit: Mapped[str | None] = mapped_column(String(50))
    reference_range: Mapped[str | None] = mapped_column(String(100))
    abnormal_flag: Mapped[str | None] = mapped_column(String(10))  # H, L, HH, LL, N
    result_status: Mapped[str] = mapped_column(String(50), nullable=False, default="final")
    ordering_provider_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("providers.provider_id"), nullable=True
    )
    collected_at: Mapped[str | None] = mapped_column(String(30))  # ISO datetime string
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    patient: Mapped["Patient"] = relationship("Patient", back_populates="lab_results")  # noqa: F821
    encounter: Mapped["Encounter"] = relationship("Encounter", back_populates="lab_results")  # noqa: F821
