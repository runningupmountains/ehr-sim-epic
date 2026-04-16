-- EHR Simulator — Epic-style schema
-- Alternative to running scripts/init_db.py
-- Usage: psql -d ehr_sim_epic -f sql/schema.sql

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- -----------------------------------------------------------------------
-- providers
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS providers (
    provider_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    npi           VARCHAR(10)  NOT NULL UNIQUE,
    first_name    VARCHAR(100) NOT NULL,
    last_name     VARCHAR(100) NOT NULL,
    specialty     VARCHAR(100),
    department    VARCHAR(100),
    phone         VARCHAR(20),
    email         VARCHAR(200)
);

-- -----------------------------------------------------------------------
-- patients
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS patients (
    patient_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    external_mrn        VARCHAR(64)  NOT NULL UNIQUE,
    first_name          VARCHAR(100) NOT NULL,
    last_name           VARCHAR(100) NOT NULL,
    dob                 VARCHAR(10)  NOT NULL,
    sex                 VARCHAR(10)  NOT NULL,
    phone               VARCHAR(20),
    email               VARCHAR(200),
    address_line1       VARCHAR(200),
    city                VARCHAR(100),
    state               CHAR(2),
    zip_code            VARCHAR(10),
    primary_provider_id UUID REFERENCES providers(provider_id),
    member_id           VARCHAR(100),
    payer_name          VARCHAR(200),
    created_at          TIMESTAMPTZ  NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_patients_last_name  ON patients(last_name);
CREATE INDEX IF NOT EXISTS idx_patients_mrn        ON patients(external_mrn);

-- -----------------------------------------------------------------------
-- encounters
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS encounters (
    encounter_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    external_csn    VARCHAR(64)  NOT NULL UNIQUE,
    patient_id      UUID NOT NULL REFERENCES patients(patient_id),
    provider_id     UUID REFERENCES providers(provider_id),
    encounter_date  VARCHAR(10)  NOT NULL,
    encounter_type  VARCHAR(100) NOT NULL,
    visit_type      VARCHAR(100),
    department      VARCHAR(100),
    facility_name   VARCHAR(200),
    reason_for_visit VARCHAR(500),
    status          VARCHAR(50)  NOT NULL DEFAULT 'completed',
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_encounters_patient ON encounters(patient_id);
CREATE INDEX IF NOT EXISTS idx_encounters_csn     ON encounters(external_csn);

-- -----------------------------------------------------------------------
-- clinical_notes
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS clinical_notes (
    note_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    encounter_id UUID NOT NULL REFERENCES encounters(encounter_id),
    patient_id   UUID NOT NULL REFERENCES patients(patient_id),
    provider_id  UUID REFERENCES providers(provider_id),
    note_type    VARCHAR(100) NOT NULL,
    title        VARCHAR(300) NOT NULL,
    body_text    TEXT         NOT NULL,
    signed_at    TIMESTAMPTZ,
    created_at   TIMESTAMPTZ  NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_notes_patient   ON clinical_notes(patient_id);
CREATE INDEX IF NOT EXISTS idx_notes_encounter ON clinical_notes(encounter_id);

-- -----------------------------------------------------------------------
-- medications
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS medications (
    medication_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id              UUID NOT NULL REFERENCES patients(patient_id),
    medication_name         VARCHAR(200) NOT NULL,
    sig                     VARCHAR(500),
    status                  VARCHAR(50)  NOT NULL DEFAULT 'active',
    start_date              VARCHAR(10),
    end_date                VARCHAR(10),
    prescribing_provider_id UUID REFERENCES providers(provider_id),
    created_at              TIMESTAMPTZ  NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_medications_patient ON medications(patient_id);

-- -----------------------------------------------------------------------
-- allergies
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS allergies (
    allergy_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID         NOT NULL REFERENCES patients(patient_id),
    allergen   VARCHAR(200) NOT NULL,
    reaction   VARCHAR(300),
    severity   VARCHAR(50),
    status     VARCHAR(50)  NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ  NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_allergies_patient ON allergies(patient_id);

-- -----------------------------------------------------------------------
-- problems
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS problems (
    problem_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id      UUID         NOT NULL REFERENCES patients(patient_id),
    diagnosis_name  VARCHAR(300) NOT NULL,
    icd10_code      VARCHAR(10),
    status          VARCHAR(50)  NOT NULL DEFAULT 'active',
    onset_date      VARCHAR(10),
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_problems_patient ON problems(patient_id);

-- -----------------------------------------------------------------------
-- lab_results
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS lab_results (
    lab_result_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id           UUID         NOT NULL REFERENCES patients(patient_id),
    encounter_id         UUID         REFERENCES encounters(encounter_id),
    test_name            VARCHAR(200) NOT NULL,
    result_value         VARCHAR(100),
    unit                 VARCHAR(50),
    reference_range      VARCHAR(100),
    abnormal_flag        VARCHAR(10),
    result_status        VARCHAR(50)  NOT NULL DEFAULT 'final',
    ordering_provider_id UUID REFERENCES providers(provider_id),
    collected_at         VARCHAR(30),
    created_at           TIMESTAMPTZ  NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_labs_patient   ON lab_results(patient_id);
CREATE INDEX IF NOT EXISTS idx_labs_encounter ON lab_results(encounter_id);

-- -----------------------------------------------------------------------
-- documents
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS documents (
    document_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id    UUID         NOT NULL REFERENCES patients(patient_id),
    encounter_id  UUID         REFERENCES encounters(encounter_id),
    document_type VARCHAR(100) NOT NULL,
    title         VARCHAR(300) NOT NULL,
    storage_key   VARCHAR(500),
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_documents_patient ON documents(patient_id);

-- -----------------------------------------------------------------------
-- vital_signs
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS vital_signs (
    vital_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    encounter_id  UUID NOT NULL REFERENCES encounters(encounter_id),
    patient_id    UUID NOT NULL REFERENCES patients(patient_id),
    height_cm     NUMERIC(6,2),
    weight_kg     NUMERIC(6,2),
    bmi           NUMERIC(5,2),
    systolic_bp   INTEGER,
    diastolic_bp  INTEGER,
    pulse         INTEGER,
    temperature_f NUMERIC(5,2),
    spo2          INTEGER,
    recorded_at   VARCHAR(30),
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_vitals_encounter ON vital_signs(encounter_id);
CREATE INDEX IF NOT EXISTS idx_vitals_patient   ON vital_signs(patient_id);

-- -----------------------------------------------------------------------
-- claims
-- -----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS claims (
    claim_id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_number           VARCHAR(64)   NOT NULL UNIQUE,
    encounter_id           UUID          NOT NULL REFERENCES encounters(encounter_id),
    patient_id             UUID          NOT NULL REFERENCES patients(patient_id),
    payer_name             VARCHAR(200),
    member_id              VARCHAR(100),
    claim_status           VARCHAR(50)   NOT NULL DEFAULT 'draft',
    service_date           VARCHAR(10)   NOT NULL,
    billed_amount          NUMERIC(10,2),
    allowed_amount         NUMERIC(10,2),
    paid_amount            NUMERIC(10,2),
    patient_responsibility NUMERIC(10,2),
    icd10_primary          VARCHAR(20),
    icd10_codes            VARCHAR(500),
    cpt_codes              VARCHAR(500),
    place_of_service_code  VARCHAR(10),
    denial_reason          VARCHAR(500),
    adjudication_date      VARCHAR(10),
    notes                  TEXT,
    created_at             TIMESTAMPTZ   NOT NULL DEFAULT now(),
    updated_at             TIMESTAMPTZ   NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_claims_encounter   ON claims(encounter_id);
CREATE INDEX IF NOT EXISTS idx_claims_patient     ON claims(patient_id);
CREATE INDEX IF NOT EXISTS idx_claims_status      ON claims(claim_status);
CREATE INDEX IF NOT EXISTS idx_claims_number      ON claims(claim_number);
