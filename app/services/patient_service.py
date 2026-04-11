import uuid

from sqlalchemy import or_
from sqlalchemy.orm import Session, selectinload

from app.models.patient import Patient


def get_patient_by_id(db: Session, patient_id: uuid.UUID) -> Patient | None:
    return (
        db.query(Patient)
        .options(selectinload(Patient.primary_provider))
        .filter(Patient.patient_id == patient_id)
        .first()
    )


def get_patient_by_mrn(db: Session, mrn: str) -> Patient | None:
    return (
        db.query(Patient)
        .options(selectinload(Patient.primary_provider))
        .filter(Patient.external_mrn == mrn)
        .first()
    )


def search_patients(
    db: Session,
    last_name: str | None = None,
    mrn: str | None = None,
    limit: int = 25,
    offset: int = 0,
) -> list[Patient]:
    query = db.query(Patient).options(selectinload(Patient.primary_provider))

    filters = []
    if last_name:
        filters.append(Patient.last_name.ilike(f"%{last_name}%"))
    if mrn:
        filters.append(Patient.external_mrn == mrn)

    if filters:
        query = query.filter(or_(*filters))

    return query.order_by(Patient.last_name, Patient.first_name).offset(offset).limit(limit).all()


def list_patients(db: Session, limit: int = 25, offset: int = 0) -> list[Patient]:
    return (
        db.query(Patient)
        .options(selectinload(Patient.primary_provider))
        .order_by(Patient.last_name, Patient.first_name)
        .offset(offset)
        .limit(limit)
        .all()
    )
