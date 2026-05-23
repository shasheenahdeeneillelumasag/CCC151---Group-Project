CREATE TABLE IF NOT EXISTS patient (
    patient_id      VARCHAR(20) PRIMARY KEY,
    first_name      VARCHAR(50) NOT NULL,
    last_name       VARCHAR(50) NOT NULL,
    birthdate       DATE NOT NULL,
    sex TEXT NOT NULL CHECK (sex IN ('Male', 'Female'))

);

-- Multivalued contact numbers
CREATE TABLE IF NOT EXISTS patient_contact (
    contact_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id      VARCHAR(20) NOT NULL,
    contact_number  VARCHAR(20) NOT NULL,

    CONSTRAINT fk_patient_contact_patient
        FOREIGN KEY (patient_id)
        REFERENCES patient(patient_id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS vaccination_shots (
    vaccine_id          VARCHAR(20) PRIMARY KEY,
    vaccination_name    VARCHAR(100) NOT NULL,
    date_administered   DATE NOT NULL,
    facility            VARCHAR(100) NOT NULL,
    dose_number         INT NOT NULL,
    schedule_date       DATE NOT NULL,
    status              VARCHAR(20) NOT NULL CHECK (status IN ('Pending', 'Completed', 'Missed')),
    patient_id          VARCHAR(20) NOT NULL,

    CONSTRAINT fk_vaccine_patient
        FOREIGN KEY (patient_id)
        REFERENCES patient(patient_id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS appointment (
    appointment_id  VARCHAR(20) PRIMARY KEY,
    appt_date       DATE NOT NULL,
    appt_time       TIME NOT NULL,
    purpose         VARCHAR(200) NOT NULL,
    clinic_name     VARCHAR(100) NOT NULL,
    status          VARCHAR(20) NOT NULL CHECK (status IN ('Scheduled', 'Completed', 'Cancelled')),
    patient_id      VARCHAR(20) NOT NULL,

    CONSTRAINT fk_appointment_patient
        FOREIGN KEY (patient_id)
        REFERENCES patient(patient_id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS visit_record (
    record_id           VARCHAR(20) PRIMARY KEY,
    visit_date          DATE NOT NULL,
    weight_kg           DECIMAL(5,2),
    blood_pressure      VARCHAR(20),
    patient_id          VARCHAR(20) NOT NULL,

    CONSTRAINT fk_visit_patient
        FOREIGN KEY (patient_id)
        REFERENCES patient(patient_id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS diagnosis (
    diagnosis_id        VARCHAR(20) PRIMARY KEY,
    diagnosis_name      VARCHAR(100) NOT NULL,
    description         TEXT,
    diagnosed_date      DATE NOT NULL,
    record_id           VARCHAR(20) NOT NULL,

    CONSTRAINT fk_diagnosis_record
        FOREIGN KEY (record_id)
        REFERENCES visit_record(record_id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS prescription (
    prescription_id     VARCHAR(20) PRIMARY KEY,
    medication_name     VARCHAR(100) NOT NULL,
    dosage              VARCHAR(50) NOT NULL,
    prescribed_date     DATE NOT NULL,
    prescribed_by       VARCHAR(100) NOT NULL,
    record_id           VARCHAR(20) NOT NULL,

    CONSTRAINT fk_prescription_record
        FOREIGN KEY (record_id)
        REFERENCES visit_record(record_id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS document (
    doc_id              VARCHAR(20) PRIMARY KEY,
    doc_filename        VARCHAR(200) NOT NULL,
    date_uploaded       DATE NOT NULL,

    vaccine_id          VARCHAR(20),
    record_id           VARCHAR(20),
    diagnosis_id        VARCHAR(20),
    prescription_id     VARCHAR(20),

    CONSTRAINT fk_document_vaccine
        FOREIGN KEY (vaccine_id)
        REFERENCES vaccination_shots(vaccine_id)
        ON DELETE SET NULL,

    CONSTRAINT fk_document_record
        FOREIGN KEY (record_id)
        REFERENCES visit_record(record_id)
        ON DELETE SET NULL,

    CONSTRAINT fk_document_diagnosis
        FOREIGN KEY (diagnosis_id)
        REFERENCES diagnosis(diagnosis_id)
        ON DELETE SET NULL,

    CONSTRAINT fk_document_prescription
        FOREIGN KEY (prescription_id)
        REFERENCES prescription(prescription_id)
        ON DELETE SET NULL,

    CONSTRAINT chk_one_parent
    CHECK (
        (
            CASE WHEN vaccine_id IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN record_id IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN diagnosis_id IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN prescription_id IS NOT NULL THEN 1 ELSE 0 END
        ) = 1
    )
);
