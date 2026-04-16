import uuid

from sqlalchemy.orm import Session

from app.models.claim import Claim
from app.schemas.claim import ClaimCreate, ClaimUpdate


def get_claim_by_id(db: Session, claim_id: uuid.UUID) -> Claim | None:
    return db.query(Claim).filter(Claim.claim_id == claim_id).first()


def get_claim_by_number(db: Session, claim_number: str) -> Claim | None:
    return db.query(Claim).filter(Claim.claim_number == claim_number).first()


def get_claims_for_encounter(
    db: Session,
    encounter_id: uuid.UUID,
    limit: int = 25,
    offset: int = 0,
) -> list[Claim]:
    return (
        db.query(Claim)
        .filter(Claim.encounter_id == encounter_id)
        .order_by(Claim.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


def get_claims_for_patient(
    db: Session,
    patient_id: uuid.UUID,
    limit: int = 50,
    offset: int = 0,
    status: str | None = None,
) -> list[Claim]:
    query = db.query(Claim).filter(Claim.patient_id == patient_id)
    if status:
        query = query.filter(Claim.claim_status == status)
    return (
        query.order_by(Claim.service_date.desc(), Claim.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


def create_claim(
    db: Session,
    encounter_id: uuid.UUID,
    patient_id: uuid.UUID,
    data: ClaimCreate,
) -> Claim:
    claim_number = f"CLM-{uuid.uuid4().hex[:8].upper()}"
    claim = Claim(
        claim_id=uuid.uuid4(),
        claim_number=claim_number,
        encounter_id=encounter_id,
        patient_id=patient_id,
        **data.model_dump(),
    )
    db.add(claim)
    db.commit()
    db.refresh(claim)
    return claim


def update_claim(db: Session, claim: Claim, data: ClaimUpdate) -> Claim:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(claim, field, value)
    db.commit()
    db.refresh(claim)
    return claim


def delete_claim(db: Session, claim: Claim) -> None:
    db.delete(claim)
    db.commit()
