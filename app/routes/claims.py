import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.deps import get_db, require_api_key
from app.schemas.claim import ClaimCreate, ClaimOut, ClaimUpdate
from app.services import claim_service
from app.services import encounter_service

router = APIRouter(
    prefix="/api/epic/v1",
    tags=["claims"],
    dependencies=[Depends(require_api_key)],
)


@router.get("/claims", response_model=list[ClaimOut])
def search_claims(
    claim_number: str | None = Query(None, description="Exact claim number, e.g. CLM-83ABA18B"),
    db: Session = Depends(get_db),
):
    """Search claims by claim_number. Returns a list (empty if not found)."""
    if claim_number:
        claim = claim_service.get_claim_by_number(db, claim_number)
        return [claim] if claim else []
    return []


@router.get("/encounters/{encounter_id}/claims", response_model=list[ClaimOut])
def list_encounter_claims(
    encounter_id: uuid.UUID,
    limit: int = Query(25, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    encounter = encounter_service.get_encounter_by_id(db, encounter_id)
    if not encounter:
        raise HTTPException(status_code=404, detail="Encounter not found")
    return claim_service.get_claims_for_encounter(db, encounter_id, limit=limit, offset=offset)


@router.post("/encounters/{encounter_id}/claims", response_model=ClaimOut, status_code=201)
def create_encounter_claim(
    encounter_id: uuid.UUID,
    body: ClaimCreate,
    db: Session = Depends(get_db),
):
    encounter = encounter_service.get_encounter_by_id(db, encounter_id)
    if not encounter:
        raise HTTPException(status_code=404, detail="Encounter not found")
    return claim_service.create_claim(db, encounter_id, encounter.patient_id, body)


@router.get("/claims/{claim_id}", response_model=ClaimOut)
def get_claim(claim_id: uuid.UUID, db: Session = Depends(get_db)):
    claim = claim_service.get_claim_by_id(db, claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    return claim


@router.patch("/claims/{claim_id}", response_model=ClaimOut)
def update_claim(
    claim_id: uuid.UUID,
    body: ClaimUpdate,
    db: Session = Depends(get_db),
):
    claim = claim_service.get_claim_by_id(db, claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    return claim_service.update_claim(db, claim, body)


@router.delete("/claims/{claim_id}", status_code=204)
def delete_claim(claim_id: uuid.UUID, db: Session = Depends(get_db)):
    claim = claim_service.get_claim_by_id(db, claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    claim_service.delete_claim(db, claim)
