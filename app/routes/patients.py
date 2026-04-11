import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.deps import get_db, require_api_key
from app.models.allergy import Allergy
from app.models.document import Document
from app.models.lab_result import LabResult
from app.schemas.allergy import AllergyOut
from app.schemas.chart import ChartOut
from app.schemas.document import DocumentOut
from app.schemas.lab_result import LabResultOut
from app.schemas.patient import PatientOut, PatientWithProviderOut
from app.services import chart_service, encounter_service, patient_service
from app.schemas.encounter import EncounterWithProviderOut
from app.schemas.clinical_note import ClinicalNoteWithProviderOut

router = APIRouter(
    prefix="/api/epic/v1/patients",
    tags=["patients"],
    dependencies=[Depends(require_api_key)],
)


@router.get("", response_model=list[PatientWithProviderOut])
def search_patients(
    last_name: str | None = Query(None, description="Partial last name search"),
    mrn: str | None = Query(None, description="Exact MRN match"),
    limit: int = Query(25, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    if last_name or mrn:
        return patient_service.search_patients(
            db, last_name=last_name, mrn=mrn, limit=limit, offset=offset
        )
    return patient_service.list_patients(db, limit=limit, offset=offset)


@router.get("/{patient_id}", response_model=PatientWithProviderOut)
def get_patient(patient_id: uuid.UUID, db: Session = Depends(get_db)):
    patient = patient_service.get_patient_by_id(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@router.get("/{patient_id}/chart", response_model=ChartOut)
def get_patient_chart(patient_id: uuid.UUID, db: Session = Depends(get_db)):
    chart = chart_service.get_full_chart(db, patient_id)
    if not chart:
        raise HTTPException(status_code=404, detail="Patient not found")
    return chart


@router.get("/{patient_id}/encounters", response_model=list[EncounterWithProviderOut])
def get_patient_encounters(
    patient_id: uuid.UUID,
    limit: int = Query(25, ge=1, le=100),
    offset: int = Query(0, ge=0),
    since: str | None = Query(None, description="ISO date (YYYY-MM-DD) to filter encounters on or after"),
    db: Session = Depends(get_db),
):
    _assert_patient_exists(db, patient_id)
    return encounter_service.get_encounters_for_patient(
        db, patient_id, limit=limit, offset=offset, since=since
    )


@router.get("/{patient_id}/notes", response_model=list[ClinicalNoteWithProviderOut])
def get_patient_notes(
    patient_id: uuid.UUID,
    limit: int = Query(25, ge=1, le=100),
    offset: int = Query(0, ge=0),
    since: str | None = Query(None, description="ISO datetime to filter notes on or after"),
    db: Session = Depends(get_db),
):
    _assert_patient_exists(db, patient_id)
    return encounter_service.get_notes_for_patient(
        db, patient_id, limit=limit, offset=offset, since=since
    )


@router.get("/{patient_id}/labs", response_model=list[LabResultOut])
def get_patient_labs(
    patient_id: uuid.UUID,
    limit: int = Query(25, ge=1, le=100),
    offset: int = Query(0, ge=0),
    since: str | None = Query(None),
    db: Session = Depends(get_db),
):
    _assert_patient_exists(db, patient_id)
    query = db.query(LabResult).filter(LabResult.patient_id == patient_id)
    if since:
        query = query.filter(LabResult.collected_at >= since)
    return query.order_by(LabResult.collected_at.desc()).offset(offset).limit(limit).all()


@router.get("/{patient_id}/allergies", response_model=list[AllergyOut])
def get_patient_allergies(
    patient_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    _assert_patient_exists(db, patient_id)
    return db.query(Allergy).filter(Allergy.patient_id == patient_id).all()


@router.get("/{patient_id}/documents", response_model=list[DocumentOut])
def get_patient_documents(
    patient_id: uuid.UUID,
    limit: int = Query(25, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    _assert_patient_exists(db, patient_id)
    return (
        db.query(Document)
        .filter(Document.patient_id == patient_id)
        .order_by(Document.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


def _assert_patient_exists(db: Session, patient_id: uuid.UUID) -> None:
    from app.models.patient import Patient
    exists = db.query(Patient.patient_id).filter(Patient.patient_id == patient_id).first()
    if not exists:
        raise HTTPException(status_code=404, detail="Patient not found")
