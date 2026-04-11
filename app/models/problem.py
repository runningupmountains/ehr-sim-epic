import uuid
from datetime import datetime

from sqlalchemy import UUID, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Problem(Base):
    __tablename__ = "problems"

    problem_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("patients.patient_id"), nullable=False
    )
    diagnosis_name: Mapped[str] = mapped_column(String(300), nullable=False)
    icd10_code: Mapped[str | None] = mapped_column(String(10))
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")
    onset_date: Mapped[str | None] = mapped_column(String(10))  # YYYY-MM-DD
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    patient: Mapped["Patient"] = relationship("Patient", back_populates="problems")  # noqa: F821
