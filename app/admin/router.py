import json
import secrets
import uuid
from datetime import date, datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, selectinload

from app.config import settings
from app.db import SessionLocal
from app.models.allergy import Allergy
from app.models.claim import Claim
from app.models.clinical_note import ClinicalNote
from app.models.document import Document
from app.models.encounter import Encounter
from app.models.lab_result import LabResult
from app.models.medication import Medication
from app.models.patient import Patient
from app.models.problem import Problem
from app.models.provider import Provider
from app.services import chart_service
from app.services.patient_service import list_patients, search_patients

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="app/templates")


# ── Helpers ────────────────────────────────────────────────────────────────

def _db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _authed(request: Request) -> bool:
    key = request.cookies.get("ehr_admin", "")
    return bool(key) and secrets.compare_digest(key, settings.admin_key)


def _redirect_login() -> RedirectResponse:
    return RedirectResponse("/admin/login", status_code=302)


def _redirect_patient(patient_id, msg: str, error: bool = False) -> RedirectResponse:
    param = "error" if error else "success"
    return RedirectResponse(
        f"/admin/patients/{patient_id}?{param}={msg.replace(' ', '+')}", status_code=302
    )


def _today() -> str:
    return date.today().isoformat()


def _all_providers(db: Session) -> list[Provider]:
    return db.query(Provider).order_by(Provider.last_name).all()


def _get_patient(db: Session, patient_id: uuid.UUID) -> Optional[Patient]:
    return (
        db.query(Patient)
        .options(selectinload(Patient.primary_provider))
        .filter(Patient.patient_id == patient_id)
        .first()
    )


# ── Auth ───────────────────────────────────────────────────────────────────

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    if _authed(request):
        return RedirectResponse("/admin", status_code=302)
    return templates.TemplateResponse("admin/login.html", {"request": request})


@router.post("/login")
def login_submit(request: Request, key: str = Form(...)):
    if secrets.compare_digest(key, settings.admin_key):
        resp = RedirectResponse("/admin", status_code=302)
        resp.set_cookie("ehr_admin", key, httponly=True, samesite="lax", max_age=86400 * 7)
        return resp
    return templates.TemplateResponse(
        "admin/login.html",
        {"request": request, "error": "Invalid admin key."},
        status_code=401,
    )


@router.get("/logout")
def logout():
    resp = RedirectResponse("/admin/login", status_code=302)
    resp.delete_cookie("ehr_admin")
    return resp


# ── Dashboard ──────────────────────────────────────────────────────────────

@router.get("", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(_db)):
    if not _authed(request):
        return _redirect_login()

    counts = {
        "patients":    db.query(Patient).count(),
        "providers":   db.query(Provider).count(),
        "encounters":  db.query(Encounter).count(),
        "notes":       db.query(ClinicalNote).count(),
        "labs":        db.query(LabResult).count(),
        "medications": db.query(Medication).count(),
    }
    recent_patients = (
        db.query(Patient)
        .options(selectinload(Patient.primary_provider))
        .order_by(Patient.created_at.desc())
        .limit(10)
        .all()
    )
    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
        "active": "dashboard",
        "counts": counts,
        "recent_patients": recent_patients,
    })


# ── Patients list ──────────────────────────────────────────────────────────

@router.get("/patients", response_class=HTMLResponse)
def patient_list(request: Request, q: str = "", db: Session = Depends(_db)):
    if not _authed(request):
        return _redirect_login()

    if q:
        # try as MRN first, then last name
        patients = search_patients(db, mrn=q if q.upper().startswith("E") else None,
                                   last_name=q if not q.upper().startswith("E") else None,
                                   limit=50)
        if not patients:
            patients = search_patients(db, last_name=q, limit=50)
    else:
        patients = list_patients(db, limit=50)

    return templates.TemplateResponse("admin/patients.html", {
        "request": request,
        "active": "patients",
        "patients": patients,
        "q": q,
        "total": len(patients),
    })


# ── New patient ────────────────────────────────────────────────────────────

@router.get("/patients/new", response_class=HTMLResponse)
def new_patient_form(request: Request, db: Session = Depends(_db)):
    if not _authed(request):
        return _redirect_login()
    return templates.TemplateResponse("admin/patient_form.html", {
        "request": request,
        "active": "patients",
        "patient": None,
        "providers": _all_providers(db),
    })


@router.post("/patients/new")
def create_patient(
    request: Request,
    external_mrn:       str = Form(...),
    first_name:         str = Form(...),
    last_name:          str = Form(...),
    dob:                str = Form(...),
    sex:                str = Form(...),
    phone:              str = Form(""),
    email:              str = Form(""),
    address_line1:      str = Form(""),
    city:               str = Form(""),
    state:              str = Form(""),
    zip_code:           str = Form(""),
    primary_provider_id: str = Form(""),
    member_id:          str = Form(""),
    payer_name:         str = Form(""),
    db: Session = Depends(_db),
):
    if not _authed(request):
        return _redirect_login()

    patient = Patient(
        patient_id=uuid.uuid4(),
        external_mrn=external_mrn.strip(),
        first_name=first_name.strip(),
        last_name=last_name.strip(),
        dob=dob,
        sex=sex,
        phone=phone.strip() or None,
        email=email.strip() or None,
        address_line1=address_line1.strip() or None,
        city=city.strip() or None,
        state=state.strip().upper() or None,
        zip_code=zip_code.strip() or None,
        primary_provider_id=uuid.UUID(primary_provider_id) if primary_provider_id else None,
        member_id=member_id.strip() or None,
        payer_name=payer_name.strip() or None,
    )
    db.add(patient)
    db.commit()
    return RedirectResponse(
        f"/admin/patients/{patient.patient_id}?success=Patient+created+successfully",
        status_code=302,
    )


# ── Patient detail ─────────────────────────────────────────────────────────

@router.get("/patients/{patient_id}", response_class=HTMLResponse)
def patient_detail(request: Request, patient_id: uuid.UUID, db: Session = Depends(_db)):
    if not _authed(request):
        return _redirect_login()

    patient = _get_patient(db, patient_id)
    if not patient:
        return RedirectResponse("/admin/patients?error=Patient+not+found", status_code=302)

    encounters = (
        db.query(Encounter)
        .options(selectinload(Encounter.provider))
        .filter(Encounter.patient_id == patient_id)
        .order_by(Encounter.encounter_date.desc())
        .all()
    )
    notes = (
        db.query(ClinicalNote)
        .options(selectinload(ClinicalNote.provider))
        .filter(ClinicalNote.patient_id == patient_id)
        .order_by(ClinicalNote.signed_at.desc())
        .all()
    )
    medications = (
        db.query(Medication)
        .filter(Medication.patient_id == patient_id)
        .order_by(Medication.start_date.desc())
        .all()
    )
    allergies  = db.query(Allergy).filter(Allergy.patient_id == patient_id).all()
    problems   = db.query(Problem).filter(Problem.patient_id == patient_id).all()
    labs = (
        db.query(LabResult)
        .filter(LabResult.patient_id == patient_id)
        .order_by(LabResult.collected_at.desc())
        .all()
    )
    documents = (
        db.query(Document)
        .filter(Document.patient_id == patient_id)
        .order_by(Document.created_at.desc())
        .all()
    )
    claims = (
        db.query(Claim)
        .filter(Claim.patient_id == patient_id)
        .order_by(Claim.service_date.desc(), Claim.created_at.desc())
        .all()
    )

    # Index child records by encounter_id string for template grouping
    def _by_enc(items, id_attr="encounter_id") -> dict[str, list]:
        d: dict[str, list] = {}
        for item in items:
            key = str(getattr(item, id_attr))
            d.setdefault(key, []).append(item)
        return d

    base_url = str(request.base_url).rstrip("/")

    return templates.TemplateResponse("admin/patient_detail.html", {
        "request":           request,
        "active":            "patients",
        "patient":           patient,
        "encounters":        encounters,
        "notes":             notes,
        "notes_by_enc":      _by_enc(notes),
        "medications":       medications,
        "allergies":         allergies,
        "problems":          problems,
        "labs":              labs,
        "labs_by_enc":       _by_enc(labs),
        "documents":         documents,
        "docs_by_enc":       _by_enc(documents),
        "claims":            claims,
        "claims_by_enc":     _by_enc(claims),
        "providers":         _all_providers(db),
        "today":             _today(),
        "base_url":          base_url,
        "api_key":           settings.api_key,
    })


# ── Edit patient ───────────────────────────────────────────────────────────

@router.get("/patients/{patient_id}/edit", response_class=HTMLResponse)
def edit_patient_form(request: Request, patient_id: uuid.UUID, db: Session = Depends(_db)):
    if not _authed(request):
        return _redirect_login()
    patient = _get_patient(db, patient_id)
    if not patient:
        return RedirectResponse("/admin/patients", status_code=302)
    return templates.TemplateResponse("admin/patient_form.html", {
        "request":   request,
        "active":    "patients",
        "patient":   patient,
        "providers": _all_providers(db),
    })


@router.post("/patients/{patient_id}/edit")
def update_patient(
    request: Request,
    patient_id: uuid.UUID,
    first_name:         str = Form(...),
    last_name:          str = Form(...),
    dob:                str = Form(...),
    sex:                str = Form(...),
    phone:              str = Form(""),
    email:              str = Form(""),
    address_line1:      str = Form(""),
    city:               str = Form(""),
    state:              str = Form(""),
    zip_code:           str = Form(""),
    primary_provider_id: str = Form(""),
    member_id:          str = Form(""),
    payer_name:         str = Form(""),
    db: Session = Depends(_db),
):
    if not _authed(request):
        return _redirect_login()

    patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
    if not patient:
        return RedirectResponse("/admin/patients", status_code=302)

    patient.first_name          = first_name.strip()
    patient.last_name           = last_name.strip()
    patient.dob                 = dob
    patient.sex                 = sex
    patient.phone               = phone.strip() or None
    patient.email               = email.strip() or None
    patient.address_line1       = address_line1.strip() or None
    patient.city                = city.strip() or None
    patient.state               = state.strip().upper() or None
    patient.zip_code            = zip_code.strip() or None
    patient.primary_provider_id = uuid.UUID(primary_provider_id) if primary_provider_id else None
    patient.member_id           = member_id.strip() or None
    patient.payer_name          = payer_name.strip() or None

    db.commit()
    return _redirect_patient(patient_id, "Demographics updated")


# ── Raw chart JSON view ────────────────────────────────────────────────────

@router.get("/patients/{patient_id}/chart", response_class=HTMLResponse)
def chart_json_view(request: Request, patient_id: uuid.UUID, db: Session = Depends(_db)):
    if not _authed(request):
        return _redirect_login()

    patient = _get_patient(db, patient_id)
    if not patient:
        return RedirectResponse("/admin/patients", status_code=302)

    chart = chart_service.get_full_chart(db, patient_id)
    if not chart:
        return RedirectResponse("/admin/patients", status_code=302)

    chart_dict = json.loads(chart.model_dump_json())
    chart_pretty = json.dumps(chart_dict, indent=2, default=str)

    return templates.TemplateResponse("admin/chart_json.html", {
        "request":      request,
        "active":       "patients",
        "patient_id":   patient_id,
        "patient_name": f"{patient.first_name} {patient.last_name}",
        "chart_json":   chart_pretty,
    })


# ── Add encounter ──────────────────────────────────────────────────────────

@router.post("/patients/{patient_id}/encounters")
def add_encounter(
    request: Request,
    patient_id:       uuid.UUID,
    encounter_date:   str = Form(...),
    encounter_type:   str = Form(...),
    visit_type:       str = Form(""),
    department:       str = Form(""),
    facility_name:    str = Form(""),
    reason_for_visit: str = Form(""),
    provider_id:      str = Form(""),
    db: Session = Depends(_db),
):
    if not _authed(request):
        return _redirect_login()

    csn = f"CSN-{uuid.uuid4().hex[:8].upper()}"
    enc = Encounter(
        encounter_id=uuid.uuid4(),
        external_csn=csn,
        patient_id=patient_id,
        provider_id=uuid.UUID(provider_id) if provider_id else None,
        encounter_date=encounter_date,
        encounter_type=encounter_type,
        visit_type=visit_type.strip() or None,
        department=department.strip() or None,
        facility_name=facility_name.strip() or None,
        reason_for_visit=reason_for_visit.strip() or None,
        status="completed",
    )
    db.add(enc)
    db.commit()
    return _redirect_patient(patient_id, f"Encounter added ({csn})")


# ── Add note ───────────────────────────────────────────────────────────────

@router.post("/patients/{patient_id}/notes")
def add_note(
    request: Request,
    patient_id:   uuid.UUID,
    encounter_id: str = Form(...),
    note_type:    str = Form(...),
    title:        str = Form(...),
    body_text:    str = Form(...),
    provider_id:  str = Form(""),
    signed_at:    str = Form(""),
    db: Session = Depends(_db),
):
    if not _authed(request):
        return _redirect_login()

    signed_dt = None
    if signed_at:
        try:
            signed_dt = datetime.fromisoformat(signed_at).replace(tzinfo=timezone.utc)
        except ValueError:
            signed_dt = datetime.now(timezone.utc)

    note = ClinicalNote(
        note_id=uuid.uuid4(),
        encounter_id=uuid.UUID(encounter_id),
        patient_id=patient_id,
        provider_id=uuid.UUID(provider_id) if provider_id else None,
        note_type=note_type,
        title=title.strip(),
        body_text=body_text.strip(),
        signed_at=signed_dt or datetime.now(timezone.utc),
    )
    db.add(note)
    db.commit()
    return _redirect_patient(patient_id, "Note added")


# ── Add medication ─────────────────────────────────────────────────────────

@router.post("/patients/{patient_id}/medications")
def add_medication(
    request: Request,
    patient_id:              uuid.UUID,
    medication_name:         str = Form(...),
    sig:                     str = Form(""),
    status:                  str = Form("active"),
    start_date:              str = Form(""),
    end_date:                str = Form(""),
    prescribing_provider_id: str = Form(""),
    db: Session = Depends(_db),
):
    if not _authed(request):
        return _redirect_login()

    med = Medication(
        medication_id=uuid.uuid4(),
        patient_id=patient_id,
        medication_name=medication_name.strip(),
        sig=sig.strip() or None,
        status=status,
        start_date=start_date or None,
        end_date=end_date or None,
        prescribing_provider_id=uuid.UUID(prescribing_provider_id) if prescribing_provider_id else None,
    )
    db.add(med)
    db.commit()
    return _redirect_patient(patient_id, f"Medication added: {medication_name}")


# ── Add allergy ────────────────────────────────────────────────────────────

@router.post("/patients/{patient_id}/allergies")
def add_allergy(
    request: Request,
    patient_id: uuid.UUID,
    allergen:   str = Form(...),
    reaction:   str = Form(""),
    severity:   str = Form("moderate"),
    status:     str = Form("active"),
    db: Session = Depends(_db),
):
    if not _authed(request):
        return _redirect_login()

    a = Allergy(
        allergy_id=uuid.uuid4(),
        patient_id=patient_id,
        allergen=allergen.strip(),
        reaction=reaction.strip() or None,
        severity=severity,
        status=status,
    )
    db.add(a)
    db.commit()
    return _redirect_patient(patient_id, f"Allergy added: {allergen}")


# ── Add problem ────────────────────────────────────────────────────────────

@router.post("/patients/{patient_id}/problems")
def add_problem(
    request: Request,
    patient_id:     uuid.UUID,
    diagnosis_name: str = Form(...),
    icd10_code:     str = Form(""),
    status:         str = Form("active"),
    onset_date:     str = Form(""),
    db: Session = Depends(_db),
):
    if not _authed(request):
        return _redirect_login()

    pr = Problem(
        problem_id=uuid.uuid4(),
        patient_id=patient_id,
        diagnosis_name=diagnosis_name.strip(),
        icd10_code=icd10_code.strip() or None,
        status=status,
        onset_date=onset_date or None,
    )
    db.add(pr)
    db.commit()
    return _redirect_patient(patient_id, f"Problem added: {diagnosis_name}")


# ── Add lab result ─────────────────────────────────────────────────────────

@router.post("/patients/{patient_id}/labs")
def add_lab(
    request: Request,
    patient_id:           uuid.UUID,
    test_name:            str = Form(...),
    result_value:         str = Form(""),
    unit:                 str = Form(""),
    reference_range:      str = Form(""),
    abnormal_flag:        str = Form("N"),
    result_status:        str = Form("final"),
    collected_at:         str = Form(""),
    ordering_provider_id: str = Form(""),
    encounter_id:         str = Form(""),
    db: Session = Depends(_db),
):
    if not _authed(request):
        return _redirect_login()

    # Normalize datetime-local to ISO string
    collected = collected_at.replace("T", " ") if collected_at else None

    lr = LabResult(
        lab_result_id=uuid.uuid4(),
        patient_id=patient_id,
        encounter_id=uuid.UUID(encounter_id) if encounter_id else None,
        test_name=test_name.strip(),
        result_value=result_value.strip() or None,
        unit=unit.strip() or None,
        reference_range=reference_range.strip() or None,
        abnormal_flag=abnormal_flag if abnormal_flag != "N" else "N",
        result_status=result_status,
        ordering_provider_id=uuid.UUID(ordering_provider_id) if ordering_provider_id else None,
        collected_at=collected,
    )
    db.add(lr)
    db.commit()
    return _redirect_patient(patient_id, f"Lab added: {test_name}")


# ── Add document ───────────────────────────────────────────────────────────

@router.post("/patients/{patient_id}/documents")
def add_document(
    request: Request,
    patient_id:    uuid.UUID,
    document_type: str = Form(...),
    title:         str = Form(...),
    storage_key:   str = Form(""),
    encounter_id:  str = Form(""),
    db: Session = Depends(_db),
):
    if not _authed(request):
        return _redirect_login()

    doc = Document(
        document_id=uuid.uuid4(),
        patient_id=patient_id,
        encounter_id=uuid.UUID(encounter_id) if encounter_id else None,
        document_type=document_type,
        title=title.strip(),
        storage_key=storage_key.strip() or None,
    )
    db.add(doc)
    db.commit()
    return _redirect_patient(patient_id, f"Document added: {title}")


# ── Claims list ───────────────────────────────────────────────────────────

@router.get("/claims", response_class=HTMLResponse)
def claims_list(request: Request, db: Session = Depends(_db)):
    if not _authed(request):
        return _redirect_login()

    claims = (
        db.query(Claim)
        .options(
            selectinload(Claim.encounter).selectinload(Encounter.provider),
            selectinload(Claim.patient),
        )
        .order_by(Claim.service_date.desc(), Claim.created_at.desc())
        .all()
    )

    # Group claims by encounter, preserving order
    from collections import OrderedDict
    enc_map: OrderedDict = OrderedDict()
    for c in claims:
        key = str(c.encounter_id)
        if key not in enc_map:
            enc_map[key] = {"encounter": c.encounter, "patient": c.patient, "claims": []}
        enc_map[key]["claims"].append(c)

    status_counts: dict[str, int] = {}
    for c in claims:
        status_counts[c.claim_status] = status_counts.get(c.claim_status, 0) + 1

    total_billed = sum(c.billed_amount for c in claims if c.billed_amount is not None)
    total_paid   = sum(c.paid_amount   for c in claims if c.paid_amount   is not None)

    return templates.TemplateResponse("admin/claims_list.html", {
        "request":       request,
        "active":        "claims",
        "enc_groups":    list(enc_map.values()),
        "total":         len(claims),
        "status_counts": status_counts,
        "total_billed":  total_billed,
        "total_paid":    total_paid,
    })


# ── Add claim ──────────────────────────────────────────────────────────────

@router.post("/patients/{patient_id}/claims")
def add_claim(
    request: Request,
    patient_id:             uuid.UUID,
    encounter_id:           str = Form(...),
    payer_name:             str = Form(""),
    member_id:              str = Form(""),
    claim_status:           str = Form("draft"),
    service_date:           str = Form(...),
    billed_amount:          str = Form(""),
    allowed_amount:         str = Form(""),
    paid_amount:            str = Form(""),
    patient_responsibility: str = Form(""),
    icd10_primary:          str = Form(""),
    icd10_codes:            str = Form(""),
    cpt_codes:              str = Form(""),
    place_of_service_code:  str = Form(""),
    denial_reason:          str = Form(""),
    adjudication_date:      str = Form(""),
    notes:                  str = Form(""),
    db: Session = Depends(_db),
):
    if not _authed(request):
        return _redirect_login()

    def _money(val: str) -> float | None:
        try:
            return float(val) if val.strip() else None
        except ValueError:
            return None

    claim_number = f"CLM-{uuid.uuid4().hex[:8].upper()}"
    claim = Claim(
        claim_id=uuid.uuid4(),
        claim_number=claim_number,
        encounter_id=uuid.UUID(encounter_id),
        patient_id=patient_id,
        payer_name=payer_name.strip() or None,
        member_id=member_id.strip() or None,
        claim_status=claim_status,
        service_date=service_date,
        billed_amount=_money(billed_amount),
        allowed_amount=_money(allowed_amount),
        paid_amount=_money(paid_amount),
        patient_responsibility=_money(patient_responsibility),
        icd10_primary=icd10_primary.strip() or None,
        icd10_codes=icd10_codes.strip() or None,
        cpt_codes=cpt_codes.strip() or None,
        place_of_service_code=place_of_service_code.strip() or None,
        denial_reason=denial_reason.strip() or None,
        adjudication_date=adjudication_date or None,
        notes=notes.strip() or None,
    )
    db.add(claim)
    db.commit()
    return _redirect_patient(patient_id, f"Claim added ({claim_number})")


@router.get("/claims/{claim_id}/edit", response_class=HTMLResponse)
def edit_claim_form(request: Request, claim_id: uuid.UUID, db: Session = Depends(_db)):
    if not _authed(request):
        return _redirect_login()

    claim = db.query(Claim).filter(Claim.claim_id == claim_id).first()
    if not claim:
        return RedirectResponse("/admin/patients", status_code=302)

    encounter = db.query(Encounter).filter(Encounter.encounter_id == claim.encounter_id).first()
    return templates.TemplateResponse("admin/claim_form.html", {
        "request":   request,
        "active":    "patients",
        "claim":     claim,
        "encounter": encounter,
    })


@router.post("/claims/{claim_id}/edit")
def update_claim(
    request: Request,
    claim_id:               uuid.UUID,
    payer_name:             str = Form(""),
    member_id:              str = Form(""),
    claim_status:           str = Form("draft"),
    service_date:           str = Form(...),
    billed_amount:          str = Form(""),
    allowed_amount:         str = Form(""),
    paid_amount:            str = Form(""),
    patient_responsibility: str = Form(""),
    icd10_primary:          str = Form(""),
    icd10_codes:            str = Form(""),
    cpt_codes:              str = Form(""),
    place_of_service_code:  str = Form(""),
    denial_reason:          str = Form(""),
    adjudication_date:      str = Form(""),
    notes:                  str = Form(""),
    db: Session = Depends(_db),
):
    if not _authed(request):
        return _redirect_login()

    def _money(val: str) -> float | None:
        try:
            return float(val) if val.strip() else None
        except ValueError:
            return None

    claim = db.query(Claim).filter(Claim.claim_id == claim_id).first()
    if not claim:
        return RedirectResponse("/admin/patients", status_code=302)

    claim.payer_name             = payer_name.strip() or None
    claim.member_id              = member_id.strip() or None
    claim.claim_status           = claim_status
    claim.service_date           = service_date
    claim.billed_amount          = _money(billed_amount)
    claim.allowed_amount         = _money(allowed_amount)
    claim.paid_amount            = _money(paid_amount)
    claim.patient_responsibility = _money(patient_responsibility)
    claim.icd10_primary          = icd10_primary.strip() or None
    claim.icd10_codes            = icd10_codes.strip() or None
    claim.cpt_codes              = cpt_codes.strip() or None
    claim.place_of_service_code  = place_of_service_code.strip() or None
    claim.denial_reason          = denial_reason.strip() or None
    claim.adjudication_date      = adjudication_date or None
    claim.notes                  = notes.strip() or None
    db.commit()

    return _redirect_patient(claim.patient_id, f"Claim {claim.claim_number} updated")


@router.post("/claims/{claim_id}/delete")
def delete_claim(request: Request, claim_id: uuid.UUID, db: Session = Depends(_db)):
    if not _authed(request):
        return _redirect_login()

    claim = db.query(Claim).filter(Claim.claim_id == claim_id).first()
    if not claim:
        return RedirectResponse("/admin/patients", status_code=302)

    patient_id = claim.patient_id
    claim_number = claim.claim_number
    db.delete(claim)
    db.commit()
    return _redirect_patient(patient_id, f"Claim {claim_number} deleted")


# ── Providers list ─────────────────────────────────────────────────────────

@router.get("/providers", response_class=HTMLResponse)
def provider_list(request: Request, db: Session = Depends(_db)):
    if not _authed(request):
        return _redirect_login()
    providers = db.query(Provider).order_by(Provider.last_name).all()
    return templates.TemplateResponse("admin/providers.html", {
        "request":   request,
        "active":    "providers",
        "providers": providers,
    })


# ── Provider detail ────────────────────────────────────────────────────────

@router.get("/providers/{provider_id}", response_class=HTMLResponse)
def provider_detail(request: Request, provider_id: uuid.UUID, db: Session = Depends(_db)):
    if not _authed(request):
        return _redirect_login()

    provider = db.query(Provider).filter(Provider.provider_id == provider_id).first()
    if not provider:
        return RedirectResponse("/admin/providers?error=Provider+not+found", status_code=302)

    encounters = (
        db.query(Encounter)
        .options(selectinload(Encounter.patient))
        .filter(Encounter.provider_id == provider_id)
        .order_by(Encounter.encounter_date.desc())
        .limit(50)
        .all()
    )
    patients = (
        db.query(Patient)
        .filter(Patient.primary_provider_id == provider_id)
        .order_by(Patient.last_name)
        .all()
    )

    return templates.TemplateResponse("admin/provider_detail.html", {
        "request":    request,
        "active":     "providers",
        "provider":   provider,
        "encounters": encounters,
        "patients":   patients,
    })


# ── Encounters list ────────────────────────────────────────────────────────

@router.get("/encounters", response_class=HTMLResponse)
def encounter_list(request: Request, db: Session = Depends(_db)):
    if not _authed(request):
        return _redirect_login()

    encounters = (
        db.query(Encounter)
        .options(selectinload(Encounter.provider), selectinload(Encounter.patient))
        .order_by(Encounter.encounter_date.desc())
        .all()
    )

    # Child records indexed by encounter_id string
    from app.models.clinical_note import ClinicalNote as _CN
    from app.models.lab_result    import LabResult    as _LR
    from app.models.document      import Document     as _Doc

    def _by_enc(items, id_attr="encounter_id") -> dict[str, list]:
        d: dict[str, list] = {}
        for item in items:
            key = str(getattr(item, id_attr))
            d.setdefault(key, []).append(item)
        return d

    notes_by_enc  = _by_enc(db.query(_CN).options(selectinload(_CN.provider)).all())
    labs_by_enc   = _by_enc(db.query(_LR).all())
    claims_by_enc = _by_enc(db.query(Claim).all())
    docs_by_enc   = _by_enc(db.query(Document).all())

    # Group encounters by patient, preserving most-recent-first order per patient
    from collections import OrderedDict
    patients_map: OrderedDict = OrderedDict()
    for enc in encounters:
        key = str(enc.patient_id)
        if key not in patients_map:
            patients_map[key] = {"patient": enc.patient, "encounters": []}
        patients_map[key]["encounters"].append(enc)

    return templates.TemplateResponse("admin/encounters.html", {
        "request":       request,
        "active":        "encounters",
        "patients_map":  list(patients_map.values()),
        "notes_by_enc":  notes_by_enc,
        "labs_by_enc":   labs_by_enc,
        "claims_by_enc": claims_by_enc,
        "docs_by_enc":   docs_by_enc,
        "total":         len(encounters),
    })
