import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.deps import get_db, require_api_key
from app.schemas.clinical_note import ClinicalNoteWithProviderOut
from app.schemas.encounter import EncounterWithProviderOut
from app.services import encounter_service

router = APIRouter(
    prefix="/api/epic/v1/encounters",
    tags=["encounters"],
    dependencies=[Depends(require_api_key)],
)


@router.get("", response_model=list[EncounterWithProviderOut])
def search_encounters(
    csn: str | None = Query(None, description="Exact CSN / encounter number, e.g. CSN-10006"),
    db: Session = Depends(get_db),
):
    """Look up an encounter by its CSN (external_csn). Returns 0 or 1 results."""
    if not csn:
        return []
    enc = encounter_service.get_encounter_by_csn(db, csn)
    return [enc] if enc else []


@router.get("/{encounter_id}", response_model=EncounterWithProviderOut)
def get_encounter(encounter_id: uuid.UUID, db: Session = Depends(get_db)):
    encounter = encounter_service.get_encounter_by_id(db, encounter_id)
    if not encounter:
        raise HTTPException(status_code=404, detail="Encounter not found")
    return encounter


@router.get("/{encounter_id}/notes", response_model=list[ClinicalNoteWithProviderOut])
def get_encounter_notes(
    encounter_id: uuid.UUID,
    limit: int = Query(25, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    encounter = encounter_service.get_encounter_by_id(db, encounter_id)
    if not encounter:
        raise HTTPException(status_code=404, detail="Encounter not found")
    return encounter_service.get_notes_for_encounter(
        db, encounter_id, limit=limit, offset=offset
    )
