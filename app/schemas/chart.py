from pydantic import BaseModel

from app.schemas.allergy import AllergyOut
from app.schemas.clinical_note import ClinicalNoteWithProviderOut
from app.schemas.document import DocumentOut
from app.schemas.encounter import EncounterWithProviderOut
from app.schemas.lab_result import LabResultOut
from app.schemas.medication import MedicationOut
from app.schemas.patient import PatientOut
from app.schemas.problem import ProblemOut
from app.schemas.provider import ProviderOut


class ChartOut(BaseModel):
    patient: PatientOut
    primary_provider: ProviderOut | None
    recent_encounters: list[EncounterWithProviderOut]
    clinical_notes: list[ClinicalNoteWithProviderOut]
    medications: list[MedicationOut]
    allergies: list[AllergyOut]
    problems: list[ProblemOut]
    lab_results: list[LabResultOut]
    documents: list[DocumentOut]
