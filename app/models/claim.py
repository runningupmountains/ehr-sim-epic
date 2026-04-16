import uuid
from datetime import datetime

from sqlalchemy import UUID, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Claim(Base):
    __tablename__ = "claims"

    claim_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    claim_number: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    encounter_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("encounters.encounter_id"), nullable=False
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("patients.patient_id"), nullable=False
    )

    # Payer / insurance
    payer_name: Mapped[str | None] = mapped_column(String(200))
    member_id: Mapped[str | None] = mapped_column(String(100))

    # Claim lifecycle
    claim_status: Mapped[str] = mapped_column(String(50), nullable=False, default="draft")
    # draft | submitted | accepted | pending | denied | paid | void

    service_date: Mapped[str] = mapped_column(String(10), nullable=False)  # YYYY-MM-DD

    # Financials
    billed_amount: Mapped[float | None] = mapped_column(Numeric(10, 2))
    allowed_amount: Mapped[float | None] = mapped_column(Numeric(10, 2))
    paid_amount: Mapped[float | None] = mapped_column(Numeric(10, 2))
    patient_responsibility: Mapped[float | None] = mapped_column(Numeric(10, 2))

    # Clinical coding
    icd10_primary: Mapped[str | None] = mapped_column(String(20))   # e.g. I10
    icd10_codes: Mapped[str | None] = mapped_column(String(500))     # comma-separated additional codes
    cpt_codes: Mapped[str | None] = mapped_column(String(500))       # comma-separated CPT codes
    place_of_service_code: Mapped[str | None] = mapped_column(String(10))

    # Adjudication
    denial_reason: Mapped[str | None] = mapped_column(String(500))
    adjudication_date: Mapped[str | None] = mapped_column(String(10))  # YYYY-MM-DD

    # Notes
    notes: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    encounter: Mapped["Encounter"] = relationship("Encounter", back_populates="claims")  # noqa: F821
    patient: Mapped["Patient"] = relationship("Patient", back_populates="claims")  # noqa: F821
