import uuid

from sqlalchemy.orm import Session, selectinload

from app.models.allergy import Allergy
from app.models.clinical_note import ClinicalNote
from app.models.document import Document
from app.models.encounter import Encounter
from app.models.lab_result import LabResult
from app.models.medication import Medication
from app.models.patient import Patient
from app.models.problem import Problem
from app.schemas.chart import ChartOut


def get_full_chart(db: Session, patient_id: uuid.UUID) -> ChartOut | None:
    patient = (
        db.query(Patient)
        .options(selectinload(Patient.primary_provider))
        .filter(Patient.patient_id == patient_id)
        .first()
    )
    if not patient:
        return None

    encounters = (
        db.query(Encounter)
        .options(selectinload(Encounter.provider))
        .filter(Encounter.patient_id == patient_id)
        .order_by(Encounter.encounter_date.desc())
        .limit(10)
        .all()
    )

    notes = (
        db.query(ClinicalNote)
        .options(selectinload(ClinicalNote.provider))
        .filter(ClinicalNote.patient_id == patient_id)
        .order_by(ClinicalNote.signed_at.desc())
        .limit(10)
        .all()
    )

    medications = (
        db.query(Medication)
        .filter(Medication.patient_id == patient_id)
        .order_by(Medication.start_date.desc())
        .all()
    )

    allergies = (
        db.query(Allergy)
        .filter(Allergy.patient_id == patient_id)
        .all()
    )

    problems = (
        db.query(Problem)
        .filter(Problem.patient_id == patient_id)
        .all()
    )

    labs = (
        db.query(LabResult)
        .filter(LabResult.patient_id == patient_id)
        .order_by(LabResult.collected_at.desc())
        .limit(25)
        .all()
    )

    documents = (
        db.query(Document)
        .filter(Document.patient_id == patient_id)
        .order_by(Document.created_at.desc())
        .all()
    )

    return ChartOut(
        patient=patient,
        primary_provider=patient.primary_provider,
        recent_encounters=encounters,
        clinical_notes=notes,
        medications=medications,
        allergies=allergies,
        problems=problems,
        lab_results=labs,
        documents=documents,
    )
