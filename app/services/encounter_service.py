import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session, selectinload

from app.models.clinical_note import ClinicalNote
from app.models.encounter import Encounter


def get_encounter_by_id(db: Session, encounter_id: uuid.UUID) -> Encounter | None:
    return (
        db.query(Encounter)
        .options(selectinload(Encounter.provider))
        .filter(Encounter.encounter_id == encounter_id)
        .first()
    )


def get_encounter_by_csn(db: Session, csn: str) -> Encounter | None:
    return (
        db.query(Encounter)
        .options(selectinload(Encounter.provider))
        .filter(Encounter.external_csn == csn)
        .first()
    )


def get_encounters_for_patient(
    db: Session,
    patient_id: uuid.UUID,
    limit: int = 25,
    offset: int = 0,
    since: str | None = None,
) -> list[Encounter]:
    query = (
        db.query(Encounter)
        .options(selectinload(Encounter.provider))
        .filter(Encounter.patient_id == patient_id)
    )
    if since:
        query = query.filter(Encounter.encounter_date >= since)
    return (
        query.order_by(Encounter.encounter_date.desc()).offset(offset).limit(limit).all()
    )


def get_notes_for_encounter(
    db: Session,
    encounter_id: uuid.UUID,
    limit: int = 25,
    offset: int = 0,
) -> list[ClinicalNote]:
    return (
        db.query(ClinicalNote)
        .options(selectinload(ClinicalNote.provider))
        .filter(ClinicalNote.encounter_id == encounter_id)
        .order_by(ClinicalNote.signed_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


def get_notes_for_patient(
    db: Session,
    patient_id: uuid.UUID,
    limit: int = 25,
    offset: int = 0,
    since: str | None = None,
) -> list[ClinicalNote]:
    query = (
        db.query(ClinicalNote)
        .options(selectinload(ClinicalNote.provider))
        .filter(ClinicalNote.patient_id == patient_id)
    )
    if since:
        since_dt = datetime.fromisoformat(since).replace(tzinfo=timezone.utc)
        query = query.filter(ClinicalNote.signed_at >= since_dt)
    return (
        query.order_by(ClinicalNote.signed_at.desc()).offset(offset).limit(limit).all()
    )
