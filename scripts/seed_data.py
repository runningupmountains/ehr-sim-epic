"""
Seed the EHR simulator database with realistic mock clinical data.

Usage:
    python scripts/seed_data.py

The seed is deterministic — running it twice on an empty database produces
the same dataset. Running it a second time on a populated database will skip
inserts that would violate the unique MRN / CSN / NPI constraints.
"""
import os
import sys
import uuid
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import SessionLocal
from app.models.allergy import Allergy
from app.models.clinical_note import ClinicalNote
from app.models.document import Document
from app.models.encounter import Encounter
from app.models.lab_result import LabResult
from app.models.medication import Medication
from app.models.patient import Patient
from app.models.problem import Problem
from app.models.provider import Provider
from app.models.claim import Claim
from app.models.vital_signs import VitalSigns

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _uid(seed: str) -> uuid.UUID:
    """Generate a deterministic UUID from a string seed."""
    return uuid.uuid5(uuid.NAMESPACE_DNS, f"ehr-sim.{seed}")


def _now() -> datetime:
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Provider definitions
# ---------------------------------------------------------------------------

PROVIDERS = [
    {
        "provider_id": _uid("provider-001"),
        "npi": "1234567890",
        "first_name": "Sarah",
        "last_name": "Nguyen",
        "specialty": "Internal Medicine",
        "department": "Primary Care",
        "phone": "555-301-1001",
        "email": "s.nguyen@fakeclinic.example",
    },
    {
        "provider_id": _uid("provider-002"),
        "npi": "2345678901",
        "first_name": "James",
        "last_name": "Okafor",
        "specialty": "Cardiology",
        "department": "Cardiology",
        "phone": "555-301-1002",
        "email": "j.okafor@fakeclinic.example",
    },
    {
        "provider_id": _uid("provider-003"),
        "npi": "3456789012",
        "first_name": "Emily",
        "last_name": "Thornton",
        "specialty": "Orthopedic Surgery",
        "department": "Orthopedics",
        "phone": "555-301-1003",
        "email": "e.thornton@fakeclinic.example",
    },
    {
        "provider_id": _uid("provider-004"),
        "npi": "4567890123",
        "first_name": "David",
        "last_name": "Kim",
        "specialty": "Dermatology",
        "department": "Dermatology",
        "phone": "555-301-1004",
        "email": "d.kim@fakeclinic.example",
    },
    {
        "provider_id": _uid("provider-005"),
        "npi": "5678901234",
        "first_name": "Maria",
        "last_name": "Santos",
        "specialty": "Family Medicine",
        "department": "Urgent Care",
        "phone": "555-301-1005",
        "email": "m.santos@fakeclinic.example",
    },
    {
        "provider_id": _uid("provider-006"),
        "npi": "6789012345",
        "first_name": "Robert",
        "last_name": "Patel",
        "specialty": "Endocrinology",
        "department": "Endocrinology",
        "phone": "555-301-1006",
        "email": "r.patel@fakeclinic.example",
    },
    {
        "provider_id": _uid("provider-007"),
        "npi": "7890123456",
        "first_name": "Angela",
        "last_name": "Morrison",
        "specialty": "Pulmonology",
        "department": "Pulmonology",
        "phone": "555-301-1007",
        "email": "a.morrison@fakeclinic.example",
    },
]

# ---------------------------------------------------------------------------
# Patient definitions
# ---------------------------------------------------------------------------
# Format: mrn suffix, first, last, dob, sex, phone, city, state, zip,
#         primary_provider_key (index into PROVIDERS list)

PATIENTS_DEF = [
    # Primary care / multi-specialty
    ("E100001", "Eleanor", "Hartley", "1955-06-14", "F", "555-201-0001", "Springfield", "IL", "62701", 0),
    ("E100002", "Marcus", "Williams", "1978-11-03", "M", "555-201-0002", "Chicago", "IL", "60601", 0),
    ("E100003", "Sofia", "Reyes", "1991-03-22", "F", "555-201-0003", "Naperville", "IL", "60540", 0),
    ("E100004", "James", "Thornton", "1951-09-07", "M", "555-201-0004", "Peoria", "IL", "61602", 1),
    ("E100005", "Priya", "Patel", "1968-12-30", "F", "555-201-0005", "Aurora", "IL", "60505", 0),
    ("E100006", "David", "Chen", "1995-07-18", "M", "555-201-0006", "Evanston", "IL", "60201", 4),
    ("E100007", "Margaret", "Foster", "1945-02-11", "F", "555-201-0007", "Rockford", "IL", "61101", 1),
    ("E100008", "Carlos", "Rivera", "1973-05-25", "M", "555-201-0008", "Joliet", "IL", "60432", 2),
    ("E100009", "Aisha", "Johnson", "1988-08-09", "F", "555-201-0009", "Bloomington", "IL", "61701", 3),
    ("E100010", "Robert", "Kim", "1961-01-14", "M", "555-201-0010", "Decatur", "IL", "62521", 1),
    ("E100011", "Patricia", "Gonzalez", "1983-04-27", "F", "555-201-0011", "Springfield", "IL", "62702", 0),
    ("E100012", "Thomas", "Anderson", "1946-10-05", "M", "555-201-0012", "Champaign", "IL", "61820", 1),
    ("E100013", "Mei", "Zhang", "2001-06-03", "F", "555-201-0013", "Urbana", "IL", "61801", 4),
    ("E100014", "Anthony", "Harris", "1970-12-19", "M", "555-201-0014", "Springfield", "IL", "62701", 0),
    ("E100015", "Linda", "Murphy", "1959-09-08", "F", "555-201-0015", "Decatur", "IL", "62526", 6),
    ("E100016", "Kevin", "Wallace", "1985-03-15", "M", "555-201-0016", "Joliet", "IL", "60435", 2),
    ("E100017", "Diane", "Scott", "1952-07-22", "F", "555-201-0017", "Peoria", "IL", "61603", 5),
    ("E100018", "Michael", "Brown", "1980-11-30", "M", "555-201-0018", "Aurora", "IL", "60506", 0),
    ("E100019", "Sandra", "Taylor", "1963-02-17", "F", "555-201-0019", "Naperville", "IL", "60563", 0),
    ("E100020", "George", "White", "1938-08-04", "M", "555-201-0020", "Chicago", "IL", "60602", 1),
    ("E100021", "Amanda", "Lewis", "1997-05-12", "F", "555-201-0021", "Evanston", "IL", "60202", 3),
    ("E100022", "Brian", "Walker", "1965-01-28", "M", "555-201-0022", "Rockford", "IL", "61102", 2),
    ("E100023", "Helen", "Hall", "1949-11-16", "F", "555-201-0023", "Champaign", "IL", "61821", 6),
    ("E100024", "Steven", "Young", "1976-09-01", "M", "555-201-0024", "Bloomington", "IL", "61702", 0),
    ("E100025", "Nancy", "Allen", "1957-04-20", "F", "555-201-0025", "Springfield", "IL", "62703", 5),
    ("E100026", "Daniel", "King", "1989-06-25", "M", "555-201-0026", "Urbana", "IL", "61802", 4),
    ("E100027", "Sharon", "Wright", "1944-03-09", "F", "555-201-0027", "Peoria", "IL", "61604", 1),
    ("E100028", "Jason", "Lopez", "1993-10-14", "M", "555-201-0028", "Aurora", "IL", "60507", 0),
    ("E100029", "Donna", "Hill", "1967-07-31", "F", "555-201-0029", "Naperville", "IL", "60564", 2),
    ("E100030", "Raymond", "Green", "1953-12-06", "M", "555-201-0030", "Chicago", "IL", "60603", 1),
]


# ---------------------------------------------------------------------------
# Clinical notes templates
# ---------------------------------------------------------------------------

def _note_primary_care(patient_first: str, patient_last: str, provider_last: str, reason: str) -> str:
    return f"""OFFICE VISIT — PRIMARY CARE

CHIEF COMPLAINT: {reason}

HISTORY OF PRESENT ILLNESS:
{patient_first} {patient_last} is a patient presenting today for {reason.lower()}. Patient reports symptom onset gradually over the past several weeks. Denies fever, chills, or recent illness. Sleep is reported as adequate. No recent travel.

REVIEW OF SYSTEMS:
Constitutional: No fever, no weight loss.
Cardiovascular: No chest pain, no palpitations.
Respiratory: No shortness of breath, no cough.
GI: No nausea, vomiting, or diarrhea.
Musculoskeletal: No joint pain or swelling.
Neurological: No headache, dizziness, or focal deficits.

PHYSICAL EXAMINATION:
General: Alert and oriented x3, in no acute distress.
Vital Signs: Documented separately.
HEENT: Normocephalic, atraumatic. PERRL. Oropharynx clear.
Cardiovascular: Regular rate and rhythm, no murmurs.
Pulmonary: Clear to auscultation bilaterally.
Abdomen: Soft, non-tender, non-distended. Normal bowel sounds.
Extremities: No edema. Pulses 2+ bilaterally.
Neurological: Cranial nerves II-XII intact. Gait normal.

ASSESSMENT AND PLAN:
1. {reason} — reviewed with patient. Updated management plan as discussed.
2. Continue current medications with adherence counseling.
3. Labs ordered as indicated. Results to be reviewed at follow-up.
4. Return to clinic in 3 months or sooner if symptoms worsen.
5. Patient verbalized understanding and agreement with plan.

Electronically signed by Dr. {provider_last}.
"""


def _note_cardiology(patient_first: str, patient_last: str, provider_last: str) -> str:
    return f"""CARDIOLOGY CONSULTATION NOTE

PATIENT: {patient_first} {patient_last}
REFERRING PROVIDER: Primary Care

CHIEF COMPLAINT: Evaluation of cardiac symptoms and ongoing cardiovascular risk management.

HISTORY OF PRESENT ILLNESS:
Patient presents for cardiology follow-up. Reports occasional exertional dyspnea on moderate activity. Denies orthopnea, PND, or lower extremity swelling at rest. No syncope or pre-syncope. Tolerating current medications without side effects.

CARDIAC HISTORY:
Known coronary artery disease. Prior myocardial infarction. Currently on appropriate secondary prevention therapy.

REVIEW OF SYSTEMS:
Cardiovascular: Exertional dyspnea as above. No chest pain at rest.
Respiratory: No resting dyspnea.
Peripheral: Trace bilateral ankle edema at end of day.

PHYSICAL EXAMINATION:
BP: 132/78 mmHg  |  HR: 68 bpm  |  RR: 16  |  SpO2: 97% RA
General: Well-appearing, no acute distress.
JVP: Not elevated.
Cardiovascular: Regular rate and rhythm. S1 S2 present. No S3 or S4. No murmurs or rubs.
Pulmonary: Clear to auscultation bilaterally. No rales or wheezes.
Abdomen: Soft, non-tender. No hepatomegaly.
Extremities: Trace bilateral pedal edema. Peripheral pulses intact.

ASSESSMENT:
1. Stable ischemic heart disease — well-controlled on current regimen.
2. Hypertension — blood pressure at goal.
3. Hyperlipidemia — continue statin therapy.

PLAN:
1. Continue aspirin, statin, beta-blocker, ACE inhibitor.
2. Echocardiogram ordered to assess left ventricular function.
3. Fasting lipid panel at next visit.
4. Encourage cardiac rehabilitation if not already enrolled.
5. Return to cardiology in 6 months. Earlier if symptoms change.

Electronically signed by Dr. {provider_last}.
"""


def _note_orthopedics(patient_first: str, patient_last: str, provider_last: str, joint: str = "knee") -> str:
    return f"""ORTHOPEDIC SURGERY NOTE

PATIENT: {patient_first} {patient_last}

CHIEF COMPLAINT: Right {joint} pain and limited range of motion.

HISTORY OF PRESENT ILLNESS:
Patient presents with worsening right {joint} pain over the past several months. Pain is 5/10 at rest and 8/10 with activity. Stairs and prolonged standing aggravate symptoms. Ice and NSAIDs provide partial relief. No prior surgery to this joint. No locking or giving way.

PHYSICAL EXAMINATION:
Right {joint.capitalize()}: Mild effusion present. Tenderness along medial joint line. Range of motion 0–110 degrees (limited by pain). McMurray test equivocal. Lachman negative. Neurovascularly intact distally.

IMAGING:
X-ray right {joint}: Medial joint space narrowing consistent with Grade II-III osteoarthritis. No fracture.

ASSESSMENT:
1. Right {joint} osteoarthritis, moderate to severe.

PLAN:
1. Intra-articular corticosteroid injection administered today.
2. Physical therapy referral for strengthening and range of motion.
3. Continue scheduled NSAIDs with gastroprotection.
4. Discussed surgical options (arthroscopy vs. total knee arthroplasty) if conservative measures fail.
5. Return in 6 weeks. MRI considered if no improvement.

Electronically signed by Dr. {provider_last}.
"""


def _note_urgent_care(patient_first: str, patient_last: str, provider_last: str, complaint: str) -> str:
    return f"""URGENT CARE VISIT NOTE

PATIENT: {patient_first} {patient_last}

CHIEF COMPLAINT: {complaint}

HISTORY OF PRESENT ILLNESS:
Patient presents to urgent care today with {complaint.lower()}. Onset approximately 2 days ago. Denies high fever above 102°F. No recent sick contacts identified. No prior episodes in the past year. No known allergies to antibiotics.

PHYSICAL EXAMINATION:
Vitals: T 99.1°F | BP 118/72 | HR 82 | RR 16 | SpO2 98% RA
General: Alert, mild discomfort, ambulatory.
HEENT: TMs clear bilaterally. Oropharynx mildly erythematous, no exudates.
Neck: Supple. Mild anterior cervical lymphadenopathy.
Lungs: Clear to auscultation.
Abdomen: Benign.

ASSESSMENT:
1. {complaint} — likely viral upper respiratory tract infection.

PLAN:
1. Supportive care: rest, hydration, analgesics as needed.
2. Return precautions discussed (worsening fever, difficulty breathing, inability to swallow).
3. No antibiotics indicated at this time.
4. Follow up with primary care if not improved in 5–7 days.

Electronically signed by Dr. {provider_last}.
"""


def _note_dermatology(patient_first: str, patient_last: str, provider_last: str) -> str:
    return f"""DERMATOLOGY OFFICE VISIT

PATIENT: {patient_first} {patient_last}

CHIEF COMPLAINT: Skin lesion evaluation and acne management.

HISTORY OF PRESENT ILLNESS:
Patient presents for evaluation of a pigmented lesion on the upper back and ongoing management of facial acne. Lesion noted approximately 6 months ago. No recent change in size, color, or border irregularity per patient report. Acne present since adolescence, partially controlled on current topical regimen.

PHYSICAL EXAMINATION:
Skin: Well-hydrated. Fitzpatrick type III.
Back lesion: 4mm symmetrical dark-brown macule, well-defined borders, uniform color, no ulceration or bleeding. Clinically consistent with benign compound nevus.
Face: Scattered closed and open comedones. Few papules. No cysts or nodules. No scarring.

ASSESSMENT:
1. Compound nevus, back — benign appearance.
2. Acne vulgaris, mild-moderate.

PLAN:
1. Back lesion: Clinical follow-up in 12 months. Patient counseled to return sooner if changes noted.
2. Acne: Continue tretinoin 0.025% topical nightly. Add benzoyl peroxide wash AM.
3. Strict sun protection discussed.
4. Return to dermatology in 12 months for full skin examination.

Electronically signed by Dr. {provider_last}.
"""


# ---------------------------------------------------------------------------
# Seed helpers
# ---------------------------------------------------------------------------

def _upsert_provider(db, data: dict) -> Provider:
    existing = db.query(Provider).filter_by(npi=data["npi"]).first()
    if existing:
        return existing
    p = Provider(**data)
    db.add(p)
    db.flush()
    return p


def _upsert_patient(db, data: dict) -> Patient:
    existing = db.query(Patient).filter_by(external_mrn=data["external_mrn"]).first()
    if existing:
        return existing
    p = Patient(**data)
    db.add(p)
    db.flush()
    return p


def _upsert_encounter(db, data: dict) -> Encounter:
    existing = db.query(Encounter).filter_by(external_csn=data["external_csn"]).first()
    if existing:
        return existing
    e = Encounter(**data)
    db.add(e)
    db.flush()
    return e


# ---------------------------------------------------------------------------
# Main seed
# ---------------------------------------------------------------------------

def seed(db) -> None:  # noqa: C901
    print("Seeding providers...")
    provider_objs: list[Provider] = []
    for pd in PROVIDERS:
        prov = _upsert_provider(db, pd)
        provider_objs.append(prov)

    print(f"  {len(provider_objs)} providers ready.")

    print("Seeding patients...")
    patient_objs: list[Patient] = []
    for idx, (mrn, first, last, dob, sex, phone, city, state, zip_code, prov_idx) in enumerate(PATIENTS_DEF):
        pdata = {
            "patient_id": _uid(f"patient-{mrn}"),
            "external_mrn": mrn,
            "first_name": first,
            "last_name": last,
            "dob": dob,
            "sex": sex,
            "phone": phone,
            "email": f"{first.lower()}.{last.lower()}@fakeemail.example",
            "address_line1": f"{100 + idx * 7} Elm Street",
            "city": city,
            "state": state,
            "zip_code": zip_code,
            "primary_provider_id": provider_objs[prov_idx].provider_id,
        }
        pat = _upsert_patient(db, pdata)
        patient_objs.append(pat)

    print(f"  {len(patient_objs)} patients ready.")

    # ------------------------------------------------------------------
    # Encounters
    # ------------------------------------------------------------------
    print("Seeding encounters...")

    encounter_specs = [
        # (patient_idx, provider_idx, csn_suffix, date, type, visit_type, dept, facility, reason, status)
        (0, 0, "CSN-10001", "2025-10-14", "Office Visit", "Follow-up", "Primary Care", "Springfield Medical Group", "Hypertension follow-up", "completed"),
        (0, 1, "CSN-10002", "2025-11-05", "Office Visit", "New Patient", "Cardiology", "Springfield Medical Group", "Cardiac evaluation", "completed"),
        (1, 0, "CSN-10003", "2025-09-22", "Office Visit", "Follow-up", "Primary Care", "Chicago Family Medicine", "Diabetes management", "completed"),
        (1, 5, "CSN-10004", "2025-12-01", "Office Visit", "Specialist", "Endocrinology", "Chicago Family Medicine", "Type 2 diabetes — HbA1c review", "completed"),
        (2, 0, "CSN-10005", "2026-01-08", "Office Visit", "New Patient", "Primary Care", "Naperville Clinic", "Annual wellness exam", "completed"),
        (3, 1, "CSN-10006", "2025-08-15", "Office Visit", "Follow-up", "Cardiology", "Peoria Heart Center", "Heart failure management", "completed"),
        (3, 6, "CSN-10007", "2025-11-20", "Office Visit", "Specialist", "Pulmonology", "Peoria Heart Center", "COPD exacerbation evaluation", "completed"),
        (4, 0, "CSN-10008", "2025-10-30", "Office Visit", "Follow-up", "Primary Care", "Aurora Health Clinic", "Hypertension and diabetes", "completed"),
        (5, 4, "CSN-10009", "2025-12-15", "Urgent Care", "Urgent Care", "Urgent Care", "Evanston Urgent Care", "Sore throat and fever", "completed"),
        (6, 1, "CSN-10010", "2025-07-03", "Office Visit", "Follow-up", "Cardiology", "Rockford Heart Institute", "Congestive heart failure — NYHA Class II", "completed"),
        (7, 2, "CSN-10011", "2025-09-10", "Office Visit", "Specialist", "Orthopedics", "Joliet Orthopedic Group", "Right knee pain", "completed"),
        (7, 2, "CSN-10012", "2025-12-02", "Procedure", "Pre-op Evaluation", "Orthopedics", "Joliet Orthopedic Group", "Pre-operative evaluation for right knee arthroplasty", "completed"),
        (8, 3, "CSN-10013", "2026-01-15", "Office Visit", "Follow-up", "Dermatology", "Bloomington Derm Associates", "Skin lesion and acne follow-up", "completed"),
        (9, 1, "CSN-10014", "2025-08-22", "Office Visit", "Follow-up", "Cardiology", "Decatur Heart Center", "Post-MI follow-up", "completed"),
        (10, 0, "CSN-10015", "2025-11-18", "Office Visit", "Annual Exam", "Primary Care", "Springfield Medical Group", "Annual physical", "completed"),
        (11, 1, "CSN-10016", "2025-10-07", "Office Visit", "Follow-up", "Cardiology", "Champaign Heart Group", "Atrial fibrillation rate control", "completed"),
        (12, 3, "CSN-10017", "2025-12-10", "Office Visit", "New Patient", "Dermatology", "Urbana Skin Center", "Eczema flare", "completed"),
        (13, 0, "CSN-10018", "2026-01-20", "Office Visit", "Follow-up", "Primary Care", "Springfield Medical Group", "Asthma management", "completed"),
        (14, 6, "CSN-10019", "2025-09-05", "Office Visit", "Follow-up", "Pulmonology", "Decatur Respiratory Center", "COPD stable follow-up", "completed"),
        (15, 2, "CSN-10020", "2025-11-25", "Office Visit", "Specialist", "Orthopedics", "Joliet Orthopedic Group", "Low back pain", "completed"),
        (16, 5, "CSN-10021", "2025-10-22", "Office Visit", "Follow-up", "Endocrinology", "Peoria Endocrine Clinic", "Hypothyroidism management", "completed"),
        (17, 0, "CSN-10022", "2026-02-03", "Office Visit", "Annual Exam", "Primary Care", "Aurora Health Clinic", "Annual wellness exam", "completed"),
        (18, 0, "CSN-10023", "2025-12-19", "Office Visit", "Follow-up", "Primary Care", "Naperville Clinic", "Anxiety and insomnia", "completed"),
        (19, 1, "CSN-10024", "2025-11-11", "Office Visit", "Follow-up", "Cardiology", "Chicago Heart Associates", "Peripheral artery disease follow-up", "completed"),
        (20, 4, "CSN-10025", "2026-01-28", "Urgent Care", "Urgent Care", "Urgent Care", "Evanston Urgent Care", "Ankle sprain", "completed"),
        (21, 3, "CSN-10026", "2025-12-08", "Office Visit", "New Patient", "Dermatology", "Bloomington Derm Associates", "Psoriasis evaluation", "completed"),
        (22, 2, "CSN-10027", "2025-10-15", "Office Visit", "Follow-up", "Orthopedics", "Rockford Orthopedic Specialists", "Shoulder impingement", "completed"),
        (23, 6, "CSN-10028", "2025-09-30", "Office Visit", "Follow-up", "Pulmonology", "Champaign Lung Center", "Pulmonary fibrosis follow-up", "completed"),
        (24, 5, "CSN-10029", "2026-02-10", "Office Visit", "Follow-up", "Endocrinology", "Springfield Endocrine", "Type 2 diabetes — quarterly review", "completed"),
        (25, 3, "CSN-10030", "2025-11-14", "Office Visit", "Follow-up", "Dermatology", "Urbana Skin Center", "Seborrheic dermatitis", "completed"),
    ]

    encounter_objs: dict[str, Encounter] = {}
    for (
        pat_idx, prov_idx, csn, date, enc_type, visit_type, dept, facility, reason, status
    ) in encounter_specs:
        edata = {
            "encounter_id": _uid(f"encounter-{csn}"),
            "external_csn": csn,
            "patient_id": patient_objs[pat_idx].patient_id,
            "provider_id": provider_objs[prov_idx].provider_id,
            "encounter_date": date,
            "encounter_type": enc_type,
            "visit_type": visit_type,
            "department": dept,
            "facility_name": facility,
            "reason_for_visit": reason,
            "status": status,
        }
        enc = _upsert_encounter(db, edata)
        encounter_objs[csn] = enc

    print(f"  {len(encounter_objs)} encounters ready.")

    # ------------------------------------------------------------------
    # Clinical Notes
    # ------------------------------------------------------------------
    print("Seeding clinical notes...")

    note_specs = [
        ("CSN-10001", _note_primary_care("Eleanor", "Hartley", "Nguyen", "Hypertension follow-up"), "Office Visit Note", "Office Visit Note — Hypertension"),
        ("CSN-10002", _note_cardiology("Eleanor", "Hartley", "Okafor"), "Cardiology Consultation", "Cardiology Consultation — Cardiac Evaluation"),
        ("CSN-10003", _note_primary_care("Marcus", "Williams", "Nguyen", "Diabetes management"), "Office Visit Note", "Office Visit Note — Diabetes Management"),
        ("CSN-10006", _note_cardiology("James", "Thornton", "Okafor"), "Cardiology Consultation", "Cardiology Consultation — Heart Failure"),
        ("CSN-10009", _note_urgent_care("David", "Chen", "Santos", "Sore throat and fever"), "Urgent Care Note", "Urgent Care Note — URI"),
        ("CSN-10010", _note_cardiology("Margaret", "Foster", "Okafor"), "Cardiology Consultation", "Cardiology Consultation — CHF"),
        ("CSN-10011", _note_orthopedics("Carlos", "Rivera", "Thornton", "knee"), "Orthopedic Note", "Orthopedic Note — Right Knee Pain"),
        ("CSN-10013", _note_dermatology("Aisha", "Johnson", "Kim"), "Dermatology Note", "Dermatology Note — Skin Lesion and Acne"),
        ("CSN-10014", _note_cardiology("Robert", "Kim", "Okafor"), "Cardiology Note", "Post-MI Follow-up Note"),
        ("CSN-10017", _note_dermatology("Mei", "Zhang", "Kim"), "Dermatology Note", "Dermatology Note — Eczema"),
        ("CSN-10020", _note_orthopedics("Kevin", "Wallace", "Thornton", "lumbar spine"), "Orthopedic Note", "Orthopedic Note — Low Back Pain"),
        ("CSN-10022", _note_primary_care("Michael", "Brown", "Nguyen", "Annual wellness exam"), "Annual Exam Note", "Annual Wellness Exam Note"),
        ("CSN-10025", _note_urgent_care("Amanda", "Lewis", "Santos", "Ankle sprain"), "Urgent Care Note", "Urgent Care Note — Ankle Sprain"),
        ("CSN-10027", _note_orthopedics("Helen", "Hall", "Thornton", "shoulder"), "Orthopedic Note", "Orthopedic Note — Shoulder Impingement"),
    ]

    note_count = 0
    for csn, body, note_type, title in note_specs:
        enc = encounter_objs.get(csn)
        if not enc:
            continue
        note_id = _uid(f"note-{csn}")
        existing = db.query(ClinicalNote).filter_by(note_id=note_id).first()
        if existing:
            continue
        note = ClinicalNote(
            note_id=note_id,
            encounter_id=enc.encounter_id,
            patient_id=enc.patient_id,
            provider_id=enc.provider_id,
            note_type=note_type,
            title=title,
            body_text=body,
            signed_at=datetime(2025, 11, 1, 14, 30, tzinfo=timezone.utc),
        )
        db.add(note)
        note_count += 1

    print(f"  {note_count} clinical notes ready.")

    # ------------------------------------------------------------------
    # Vital signs (for selected encounters)
    # ------------------------------------------------------------------
    print("Seeding vital signs...")

    vital_specs = [
        ("CSN-10001", 0, 165.0, 78.2, 28.8, 148, 88, 74, 98.2, 97),
        ("CSN-10002", 0, 165.0, 78.2, 28.8, 132, 78, 68, 98.0, 97),
        ("CSN-10003", 1, 178.0, 95.0, 30.0, 136, 84, 80, 98.6, 98),
        ("CSN-10006", 3, 170.0, 92.0, 31.8, 140, 90, 76, 98.4, 95),
        ("CSN-10009", 5, 182.0, 80.5, 24.3, 118, 72, 82, 99.1, 98),
        ("CSN-10010", 6, 158.0, 84.0, 33.7, 144, 92, 84, 98.8, 94),
        ("CSN-10011", 7, 175.0, 102.0, 33.3, 128, 80, 72, 98.6, 99),
        ("CSN-10013", 8, 163.0, 58.0, 21.8, 112, 70, 68, 98.2, 100),
        ("CSN-10014", 9, 172.0, 88.0, 29.7, 138, 82, 70, 98.4, 97),
    ]

    vital_count = 0
    for csn, pat_idx, h, w, bmi, sbp, dbp, pulse, temp, spo2 in vital_specs:
        enc = encounter_objs.get(csn)
        if not enc:
            continue
        vital_id = _uid(f"vital-{csn}")
        existing = db.query(VitalSigns).filter_by(vital_id=vital_id).first()
        if existing:
            continue
        vs = VitalSigns(
            vital_id=vital_id,
            encounter_id=enc.encounter_id,
            patient_id=patient_objs[pat_idx].patient_id,
            height_cm=h,
            weight_kg=w,
            bmi=bmi,
            systolic_bp=sbp,
            diastolic_bp=dbp,
            pulse=pulse,
            temperature_f=temp,
            spo2=spo2,
            recorded_at=enc.encounter_date + "T10:00:00",
        )
        db.add(vs)
        vital_count += 1

    print(f"  {vital_count} vital sign records ready.")

    # ------------------------------------------------------------------
    # Medications
    # ------------------------------------------------------------------
    print("Seeding medications...")

    med_specs = [
        # (patient_idx, name, sig, status, start, end)
        (0, "Lisinopril 10 mg tablet", "Take 1 tablet by mouth daily", "active", "2022-03-01", None),
        (0, "Amlodipine 5 mg tablet", "Take 1 tablet by mouth daily", "active", "2023-06-15", None),
        (0, "Atorvastatin 40 mg tablet", "Take 1 tablet by mouth at bedtime", "active", "2022-03-01", None),
        (0, "Aspirin 81 mg tablet", "Take 1 tablet by mouth daily", "active", "2021-01-10", None),
        (1, "Metformin 1000 mg tablet", "Take 1 tablet by mouth twice daily with meals", "active", "2020-05-12", None),
        (1, "Empagliflozin 10 mg tablet", "Take 1 tablet by mouth daily in the morning", "active", "2023-09-01", None),
        (1, "Lisinopril 20 mg tablet", "Take 1 tablet by mouth daily", "active", "2021-11-03", None),
        (1, "Atorvastatin 80 mg tablet", "Take 1 tablet by mouth at bedtime", "active", "2020-05-12", None),
        (3, "Carvedilol 12.5 mg tablet", "Take 1 tablet by mouth twice daily", "active", "2019-04-20", None),
        (3, "Furosemide 40 mg tablet", "Take 1 tablet by mouth every morning", "active", "2020-08-01", None),
        (3, "Spironolactone 25 mg tablet", "Take 1 tablet by mouth daily", "active", "2020-08-01", None),
        (3, "Tiotropium 18 mcg inhaler", "Inhale 1 capsule via HandiHaler daily", "active", "2021-02-14", None),
        (4, "Losartan 50 mg tablet", "Take 1 tablet by mouth daily", "active", "2022-07-01", None),
        (4, "Metformin 500 mg tablet", "Take 1 tablet by mouth twice daily", "active", "2023-01-15", None),
        (4, "Glipizide 5 mg tablet", "Take 1 tablet by mouth daily before breakfast", "active", "2023-01-15", None),
        (6, "Sacubitril/Valsartan 49/51 mg tablet", "Take 1 tablet by mouth twice daily", "active", "2021-03-10", None),
        (6, "Carvedilol 25 mg tablet", "Take 1 tablet by mouth twice daily", "active", "2019-06-01", None),
        (6, "Furosemide 80 mg tablet", "Take 1 tablet by mouth every morning", "active", "2020-01-20", None),
        (6, "Metolazone 2.5 mg tablet", "Take 1 tablet by mouth as directed for fluid overload", "active", "2022-09-01", None),
        (7, "Naproxen 500 mg tablet", "Take 1 tablet by mouth twice daily with food", "active", "2025-09-10", None),
        (7, "Pantoprazole 40 mg tablet", "Take 1 tablet by mouth daily before breakfast", "active", "2025-09-10", None),
        (9, "Aspirin 81 mg tablet", "Take 1 tablet by mouth daily", "active", "2023-08-22", None),
        (9, "Metoprolol succinate 50 mg tablet", "Take 1 tablet by mouth daily", "active", "2023-08-22", None),
        (9, "Atorvastatin 80 mg tablet", "Take 1 tablet by mouth at bedtime", "active", "2023-08-22", None),
        (9, "Clopidogrel 75 mg tablet", "Take 1 tablet by mouth daily", "active", "2023-08-22", None),
        (11, "Digoxin 0.125 mg tablet", "Take 1 tablet by mouth daily", "active", "2020-10-07", None),
        (11, "Apixaban 5 mg tablet", "Take 1 tablet by mouth twice daily", "active", "2021-02-14", None),
        (11, "Metoprolol tartrate 25 mg tablet", "Take 1 tablet by mouth twice daily", "active", "2020-10-07", None),
        (14, "Tiotropium 18 mcg inhaler", "Inhale 1 capsule via HandiHaler daily", "active", "2018-06-01", None),
        (14, "Albuterol HFA inhaler", "Inhale 2 puffs by mouth every 4-6 hours as needed", "active", "2018-06-01", None),
        (16, "Levothyroxine 88 mcg tablet", "Take 1 tablet by mouth daily on an empty stomach", "active", "2019-03-15", None),
        (24, "Levothyroxine 75 mcg tablet", "Take 1 tablet by mouth daily on an empty stomach", "active", "2021-07-20", None),
        (5, "Ibuprofen 400 mg tablet", "Take 1 tablet by mouth every 6 hours as needed for pain", "active", "2025-12-15", "2025-12-22"),
        (13, "Albuterol HFA inhaler", "Inhale 2 puffs by mouth every 4-6 hours as needed", "active", "2023-04-10", None),
        (13, "Fluticasone 110 mcg inhaler", "Inhale 2 puffs by mouth twice daily", "active", "2023-04-10", None),
    ]

    med_count = 0
    for pat_idx, name, sig, status, start, end in med_specs:
        pat = patient_objs[pat_idx]
        med_id = _uid(f"med-{pat.external_mrn}-{name[:20]}")
        existing = db.query(Medication).filter_by(medication_id=med_id).first()
        if existing:
            continue
        med = Medication(
            medication_id=med_id,
            patient_id=pat.patient_id,
            medication_name=name,
            sig=sig,
            status=status,
            start_date=start,
            end_date=end,
            prescribing_provider_id=pat.primary_provider_id,
        )
        db.add(med)
        med_count += 1

    print(f"  {med_count} medications ready.")

    # ------------------------------------------------------------------
    # Allergies
    # ------------------------------------------------------------------
    print("Seeding allergies...")

    allergy_specs = [
        (0, "Penicillin", "Rash, urticaria", "moderate", "active"),
        (1, "Sulfa drugs", "Anaphylaxis", "severe", "active"),
        (3, "Aspirin", "Bronchospasm", "severe", "active"),
        (4, "Codeine", "Nausea and vomiting", "mild", "active"),
        (5, "Latex", "Contact dermatitis", "mild", "active"),
        (6, "ACE inhibitors", "Angioedema", "severe", "active"),
        (7, "NSAIDs", "GI bleeding", "moderate", "active"),
        (9, "Contrast dye (iodine)", "Hives, pruritis", "moderate", "active"),
        (11, "Warfarin", "Bleeding complications", "moderate", "inactive"),
        (13, "Peanuts", "Anaphylaxis", "severe", "active"),
        (16, "Shellfish", "Hives", "mild", "active"),
        (2, "NKDA", None, None, "active"),
        (8, "NKDA", None, None, "active"),
        (10, "NKDA", None, None, "active"),
    ]

    allergy_count = 0
    for pat_idx, allergen, reaction, severity, status in allergy_specs:
        pat = patient_objs[pat_idx]
        allergy_id = _uid(f"allergy-{pat.external_mrn}-{allergen[:15]}")
        existing = db.query(Allergy).filter_by(allergy_id=allergy_id).first()
        if existing:
            continue
        a = Allergy(
            allergy_id=allergy_id,
            patient_id=pat.patient_id,
            allergen=allergen,
            reaction=reaction,
            severity=severity,
            status=status,
        )
        db.add(a)
        allergy_count += 1

    print(f"  {allergy_count} allergies ready.")

    # ------------------------------------------------------------------
    # Problems
    # ------------------------------------------------------------------
    print("Seeding problems...")

    problem_specs = [
        (0, "Essential hypertension", "I10", "active", "2018-06-01"),
        (0, "Hyperlipidemia", "E78.5", "active", "2019-03-01"),
        (0, "Osteoarthritis, bilateral knees", "M17.3", "active", "2022-11-01"),
        (1, "Type 2 diabetes mellitus", "E11.9", "active", "2020-05-12"),
        (1, "Essential hypertension", "I10", "active", "2019-08-01"),
        (1, "Obesity, class I", "E66.01", "active", "2020-05-12"),
        (1, "Hyperlipidemia", "E78.5", "active", "2019-08-01"),
        (3, "Chronic systolic heart failure", "I50.20", "active", "2019-04-20"),
        (3, "Chronic obstructive pulmonary disease", "J44.1", "active", "2018-02-01"),
        (3, "Hypertension", "I10", "active", "2015-07-01"),
        (3, "Hyperlipidemia", "E78.5", "active", "2015-07-01"),
        (4, "Essential hypertension", "I10", "active", "2020-09-01"),
        (4, "Type 2 diabetes mellitus", "E11.9", "active", "2022-11-15"),
        (5, "Viral upper respiratory infection", "J06.9", "resolved", "2025-12-15"),
        (6, "Congestive heart failure, diastolic, chronic", "I50.30", "active", "2018-09-01"),
        (6, "Atrial fibrillation, persistent", "I48.11", "active", "2019-01-01"),
        (7, "Osteoarthritis, right knee", "M17.11", "active", "2024-04-01"),
        (7, "Obesity, class II", "E66.09", "active", "2022-01-01"),
        (8, "Acne vulgaris", "L70.0", "active", "2020-08-01"),
        (8, "Compound nevus, back", "D22.5", "active", "2025-07-01"),
        (9, "Coronary artery disease", "I25.10", "active", "2023-08-22"),
        (9, "Hyperlipidemia", "E78.5", "active", "2020-01-01"),
        (9, "Hypertension", "I10", "active", "2021-05-01"),
        (11, "Atrial fibrillation, paroxysmal", "I48.0", "active", "2020-10-07"),
        (11, "Coronary artery disease", "I25.10", "active", "2018-03-01"),
        (13, "Asthma, moderate persistent", "J45.40", "active", "2023-04-10"),
        (14, "Chronic obstructive pulmonary disease", "J44.1", "active", "2018-06-01"),
        (14, "Hypertension", "I10", "active", "2016-01-01"),
        (16, "Hypothyroidism", "E03.9", "active", "2019-03-15"),
        (24, "Hypothyroidism", "E03.9", "active", "2021-07-20"),
        (24, "Type 2 diabetes mellitus", "E11.9", "active", "2022-02-01"),
        (15, "Lumbar disc herniation", "M51.16", "active", "2024-08-01"),
        (22, "Shoulder impingement syndrome, right", "M75.1", "active", "2025-09-01"),
        (23, "Idiopathic pulmonary fibrosis", "J84.112", "active", "2022-05-01"),
        (12, "Atopic dermatitis", "L20.9", "active", "2019-01-01"),
    ]

    problem_count = 0
    for pat_idx, dx_name, icd10, status, onset in problem_specs:
        pat = patient_objs[pat_idx]
        problem_id = _uid(f"problem-{pat.external_mrn}-{icd10}")
        existing = db.query(Problem).filter_by(problem_id=problem_id).first()
        if existing:
            continue
        pr = Problem(
            problem_id=problem_id,
            patient_id=pat.patient_id,
            diagnosis_name=dx_name,
            icd10_code=icd10,
            status=status,
            onset_date=onset,
        )
        db.add(pr)
        problem_count += 1

    print(f"  {problem_count} problems ready.")

    # ------------------------------------------------------------------
    # Lab results
    # ------------------------------------------------------------------
    print("Seeding lab results...")

    lab_specs = [
        # (patient_idx, csn_or_None, test_name, result, unit, ref_range, flag, status, collected_at, ordering_provider_idx)
        (0, "CSN-10001", "Hemoglobin A1c", "5.8", "%", "4.0–5.6", "H", "final", "2025-10-14T09:00", 0),
        (0, "CSN-10001", "BMP - Sodium", "141", "mEq/L", "136–145", "N", "final", "2025-10-14T09:00", 0),
        (0, "CSN-10001", "BMP - Potassium", "4.1", "mEq/L", "3.5–5.0", "N", "final", "2025-10-14T09:00", 0),
        (0, "CSN-10001", "BMP - Creatinine", "0.9", "mg/dL", "0.6–1.2", "N", "final", "2025-10-14T09:00", 0),
        (0, "CSN-10002", "Lipid Panel - LDL", "98", "mg/dL", "<100", "N", "final", "2025-11-05T08:30", 1),
        (0, "CSN-10002", "Lipid Panel - HDL", "52", "mg/dL", ">40", "N", "final", "2025-11-05T08:30", 1),
        (1, "CSN-10003", "Hemoglobin A1c", "8.1", "%", "4.0–5.6", "HH", "final", "2025-09-22T08:00", 0),
        (1, "CSN-10003", "Fasting Glucose", "182", "mg/dL", "70–100", "H", "final", "2025-09-22T08:00", 0),
        (1, "CSN-10003", "BMP - eGFR", "74", "mL/min/1.73m²", "≥60", "N", "final", "2025-09-22T08:00", 0),
        (1, "CSN-10004", "Hemoglobin A1c", "7.8", "%", "4.0–5.6", "H", "final", "2025-12-01T08:30", 5),
        (3, "CSN-10006", "BNP", "420", "pg/mL", "<100", "H", "final", "2025-08-15T07:30", 1),
        (3, "CSN-10006", "BMP - Creatinine", "1.4", "mg/dL", "0.7–1.3", "H", "final", "2025-08-15T07:30", 1),
        (3, "CSN-10006", "BMP - Potassium", "4.8", "mEq/L", "3.5–5.0", "N", "final", "2025-08-15T07:30", 1),
        (3, "CSN-10007", "Spirometry - FEV1", "58", "% predicted", ">80%", "L", "final", "2025-11-20T10:00", 6),
        (6, "CSN-10010", "BNP", "780", "pg/mL", "<100", "HH", "final", "2025-07-03T07:00", 1),
        (6, "CSN-10010", "BMP - Creatinine", "1.6", "mg/dL", "0.6–1.1", "H", "final", "2025-07-03T07:00", 1),
        (9, "CSN-10014", "Lipid Panel - LDL", "71", "mg/dL", "<70", "H", "final", "2025-08-22T08:00", 1),
        (9, "CSN-10014", "Troponin I", "0.01", "ng/mL", "<0.04", "N", "final", "2025-08-22T08:00", 1),
        (9, "CSN-10014", "CBC - WBC", "7.2", "K/µL", "4.5–11.0", "N", "final", "2025-08-22T08:00", 1),
        (11, "CSN-10016", "TSH", "2.1", "mIU/L", "0.4–4.0", "N", "final", "2025-10-07T09:00", 1),
        (11, "CSN-10016", "Digoxin level", "0.9", "ng/mL", "0.5–2.0", "N", "final", "2025-10-07T09:00", 1),
        (4, "CSN-10008", "Hemoglobin A1c", "7.2", "%", "4.0–5.6", "H", "final", "2025-10-30T08:00", 0),
        (4, "CSN-10008", "BMP - Creatinine", "1.0", "mg/dL", "0.6–1.2", "N", "final", "2025-10-30T08:00", 0),
        (14, "CSN-10019", "Spirometry - FEV1", "52", "% predicted", ">80%", "L", "final", "2025-09-05T10:00", 6),
        (16, "CSN-10021", "TSH", "6.8", "mIU/L", "0.4–4.0", "H", "final", "2025-10-22T08:30", 5),
        (16, "CSN-10021", "Free T4", "0.7", "ng/dL", "0.8–1.8", "L", "final", "2025-10-22T08:30", 5),
        (24, "CSN-10029", "Hemoglobin A1c", "6.9", "%", "4.0–5.6", "H", "final", "2026-02-10T08:00", 5),
        (24, "CSN-10029", "TSH", "2.4", "mIU/L", "0.4–4.0", "N", "final", "2026-02-10T08:00", 5),
        (23, "CSN-10028", "Pulmonary Function - DLCO", "48", "% predicted", ">70%", "L", "final", "2025-09-30T10:00", 6),
    ]

    lab_count = 0
    for (
        pat_idx, csn, test_name, result_val, unit, ref_range, flag, status, collected_at, prov_idx
    ) in lab_specs:
        pat = patient_objs[pat_idx]
        lab_id = _uid(f"lab-{pat.external_mrn}-{csn}-{test_name[:15]}")
        existing = db.query(LabResult).filter_by(lab_result_id=lab_id).first()
        if existing:
            continue
        enc = encounter_objs.get(csn)
        lr = LabResult(
            lab_result_id=lab_id,
            patient_id=pat.patient_id,
            encounter_id=enc.encounter_id if enc else None,
            test_name=test_name,
            result_value=result_val,
            unit=unit,
            reference_range=ref_range,
            abnormal_flag=flag,
            result_status=status,
            ordering_provider_id=provider_objs[prov_idx].provider_id,
            collected_at=collected_at,
        )
        db.add(lr)
        lab_count += 1

    print(f"  {lab_count} lab results ready.")

    # ------------------------------------------------------------------
    # Documents
    # ------------------------------------------------------------------
    print("Seeding documents...")

    doc_specs = [
        # (patient_idx, csn_or_None, doc_type, title, storage_key)
        (0, None, "CCD Summary", "Continuity of Care Document — Eleanor Hartley", "docs/E100001/ccd-2025-11.xml"),
        (1, "CSN-10003", "Referral", "Endocrinology Referral — Marcus Williams", "docs/E100002/referral-endo-2025-09.pdf"),
        (3, "CSN-10006", "Discharge Summary", "Discharge Summary — CHF Exacerbation", "docs/E100004/discharge-2025-08.pdf"),
        (3, None, "CCD Summary", "Continuity of Care Document — James Thornton", "docs/E100004/ccd-2025-11.xml"),
        (6, "CSN-10010", "Discharge Summary", "Discharge Summary — Decompensated CHF", "docs/E100007/discharge-2025-07.pdf"),
        (7, "CSN-10012", "Prior Authorization", "Prior Auth — Right Total Knee Arthroplasty", "docs/E100008/prior-auth-tka-2025-12.pdf"),
        (7, "CSN-10011", "Radiology Report", "Right Knee X-Ray Report", "docs/E100008/xray-right-knee-2025-09.pdf"),
        (9, "CSN-10014", "Cardiology Report", "Echocardiogram Report — Robert Kim", "docs/E100010/echo-2025-08.pdf"),
        (9, None, "CCD Summary", "Continuity of Care Document — Robert Kim", "docs/E100010/ccd-2025-08.xml"),
        (11, "CSN-10016", "ECG Report", "12-Lead ECG Report — Atrial Fibrillation", "docs/E100012/ecg-2025-10.pdf"),
        (4, "CSN-10008", "Referral", "Endocrinology Referral — Priya Patel", "docs/E100005/referral-endo-2025-10.pdf"),
        (14, "CSN-10019", "Pulmonary Function Test", "PFT Report — Spirometry", "docs/E100015/pft-2025-09.pdf"),
        (23, "CSN-10028", "Pulmonary Function Test", "PFT with DLCO — Pulmonary Fibrosis", "docs/E100024/pft-dlco-2025-09.pdf"),
        (16, "CSN-10021", "Lab Report", "Thyroid Panel — Hypothyroidism Follow-up", "docs/E100017/thyroid-labs-2025-10.pdf"),
    ]

    doc_count = 0
    for pat_idx, csn, doc_type, title, storage_key in doc_specs:
        pat = patient_objs[pat_idx]
        doc_id = _uid(f"doc-{pat.external_mrn}-{title[:20]}")
        existing = db.query(Document).filter_by(document_id=doc_id).first()
        if existing:
            continue
        enc = encounter_objs.get(csn) if csn else None
        doc = Document(
            document_id=doc_id,
            patient_id=pat.patient_id,
            encounter_id=enc.encounter_id if enc else None,
            document_type=doc_type,
            title=title,
            storage_key=storage_key,
        )
        db.add(doc)
        doc_count += 1

    print(f"  {doc_count} documents ready.")

    # ------------------------------------------------------------------
    # Claims
    # ------------------------------------------------------------------
    print("Seeding claims...")

    # (patient_idx, csn, payer, member_id, status, service_date,
    #  billed, allowed, paid, patient_resp,
    #  icd10_primary, icd10_codes, cpt_codes, pos_code,
    #  denial_reason, adjudication_date)
    claim_specs = [
        # Eleanor Hartley — hypertension follow-up, paid
        (0, "CSN-10001", "BlueCross BlueShield PPO", "MBR-00100001", "paid",
         "2025-10-14", 250.00, 195.00, 156.00, 39.00,
         "I10", "Z87.39", "99213", "11", None, "2025-11-01"),
        # Eleanor Hartley — cardiology, accepted
        (0, "CSN-10002", "BlueCross BlueShield PPO", "MBR-00100001", "accepted",
         "2025-11-05", 480.00, 360.00, None, None,
         "I25.10", "Z87.39", "99214,93000", "11", None, None),
        # Marcus Williams — diabetes, paid
        (1, "CSN-10003", "Aetna HMO", "MBR-00100002", "paid",
         "2025-09-22", 300.00, 230.00, 184.00, 46.00,
         "E11.9", "E11.65,Z96.641", "99213", "11", None, "2025-10-15"),
        # Marcus Williams — endocrinology, submitted
        (1, "CSN-10004", "Aetna HMO", "MBR-00100002", "submitted",
         "2025-12-01", 350.00, None, None, None,
         "E11.9", None, "99214", "11", None, None),
        # James Thornton — heart failure, paid
        (3, "CSN-10006", "Medicare Part B", "1EG4-TE5-MK72", "paid",
         "2025-08-15", 520.00, 415.00, 332.00, 83.00,
         "I50.9", "I25.10,N18.3", "99215,93306", "11", None, "2025-09-10"),
        # Margaret Foster — CHF, denied
        (6, "CSN-10010", "Medicare Advantage", "MBR-00100007", "denied",
         "2025-07-03", 620.00, 0.00, 0.00, 0.00,
         "I50.33", "I25.10,E11.9", "99215,93306", "11",
         "Pre-authorization not obtained for echocardiogram", "2025-08-01"),
        # Carlos Rivera — orthopedics, paid
        (7, "CSN-10011", "United Healthcare PPO", "MBR-00100008", "paid",
         "2025-09-10", 400.00, 310.00, 248.00, 62.00,
         "M17.11", None, "99213,73562", "11", None, "2025-10-05"),
        # Carlos Rivera — pre-op, pending
        (7, "CSN-10012", "United Healthcare PPO", "MBR-00100008", "pending",
         "2025-12-02", 550.00, None, None, None,
         "M17.11", "Z96.641", "99215,27447", "11", None, None),
        # Robert Kim — post-MI follow-up, paid
        (9, "CSN-10014", "Cigna PPO", "MBR-00100010", "paid",
         "2025-08-22", 390.00, 295.00, 236.00, 59.00,
         "I25.10", "Z82.49", "99214,93000", "11", None, "2025-09-18"),
        # Thomas Anderson — atrial fibrillation, paid
        (11, "CSN-10016", "Medicare Part B", "2GT5-FF9-LJ41", "paid",
         "2025-10-07", 430.00, 344.00, 275.00, 69.00,
         "I48.91", "I50.9", "99214,93000", "11", None, "2025-11-02"),
        # Priya Patel — hypertension+diabetes, submitted
        (4, "CSN-10008", "Aetna HMO", "MBR-00100005", "submitted",
         "2025-10-30", 310.00, None, None, None,
         "I10", "E11.9", "99213", "11", None, None),
        # Linda Murphy — COPD follow-up, paid
        (14, "CSN-10019", "Medicare Part B", "3HK7-AA2-PP19", "paid",
         "2025-09-05", 360.00, 288.00, 230.00, 58.00,
         "J44.1", None, "99213,94010", "11", None, "2025-10-01"),
        # Steven Young — diabetes quarterly, draft
        (24, "CSN-10029", "BlueCross BlueShield PPO", "MBR-00100025", "draft",
         "2026-02-10", 295.00, None, None, None,
         "E11.9", "E03.9", "99213", "11", None, None),
    ]

    claim_count = 0
    for (
        pat_idx, csn, payer, member_id, status, service_date,
        billed, allowed, paid, pat_resp,
        icd10_primary, icd10_codes, cpt_codes, pos_code,
        denial_reason, adj_date
    ) in claim_specs:
        pat = patient_objs[pat_idx]
        enc = encounter_objs.get(csn)
        if not enc:
            continue
        claim_id = _uid(f"claim-{pat.external_mrn}-{csn}")
        existing = db.query(Claim).filter_by(claim_id=claim_id).first()
        if existing:
            continue
        claim_number = f"CLM-{claim_id.hex[:8].upper()}"
        claim = Claim(
            claim_id=claim_id,
            claim_number=claim_number,
            encounter_id=enc.encounter_id,
            patient_id=pat.patient_id,
            payer_name=payer,
            member_id=member_id,
            claim_status=status,
            service_date=service_date,
            billed_amount=billed,
            allowed_amount=allowed,
            paid_amount=paid,
            patient_responsibility=pat_resp,
            icd10_primary=icd10_primary,
            icd10_codes=icd10_codes,
            cpt_codes=cpt_codes,
            place_of_service_code=pos_code,
            denial_reason=denial_reason,
            adjudication_date=adj_date,
        )
        db.add(claim)
        claim_count += 1

    print(f"  {claim_count} claims ready.")

    db.commit()
    print("\nSeed complete.")


def main():
    db = SessionLocal()
    try:
        seed(db)
    except Exception as e:
        db.rollback()
        print(f"\nSeed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
