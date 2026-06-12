PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS patient (
    patient_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_code    VARCHAR(10) NOT NULL UNIQUE, -- P001, P002

    first_name      VARCHAR(50) NOT NULL,
    last_name       VARCHAR(50) NOT NULL,
    birthdate       DATE NOT NULL,

    sex TEXT NOT NULL
        CHECK (sex IN ('Male', 'Female'))
);

CREATE TABLE IF NOT EXISTS patient_contact (
    contact_id      INTEGER PRIMARY KEY AUTOINCREMENT,

    patient_id      INTEGER NOT NULL,
    contact_number  VARCHAR(20) NOT NULL,

    FOREIGN KEY (patient_id)
        REFERENCES patient(patient_id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS vaccination_shots (
    vaccine_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    vaccine_code        VARCHAR(10) NOT NULL UNIQUE, -- V001

    vaccination_name    VARCHAR(100) NOT NULL,
    date_administered   DATE,
    facility            VARCHAR(100) NOT NULL,
    dose_number         INTEGER NOT NULL,

    schedule_date       DATE,
    
    status VARCHAR(20) NOT NULL
        CHECK (status IN ('Pending', 'Completed', 'Missed')),

    patient_id          INTEGER NOT NULL,

    FOREIGN KEY (patient_id)
        REFERENCES patient(patient_id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS appointment (
    appointment_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    appointment_code VARCHAR(10) NOT NULL UNIQUE, -- A001

    appt_date       DATE NOT NULL,
    appt_time       TIME NOT NULL,

    purpose         VARCHAR(200) NOT NULL,
    clinic_name     VARCHAR(100) NOT NULL,

    status VARCHAR(20) NOT NULL
        CHECK (status IN ('Scheduled', 'Completed', 'Cancelled')),

    patient_id      INTEGER NOT NULL,

    FOREIGN KEY (patient_id)
        REFERENCES patient(patient_id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS visit_record (
    record_id           INTEGER PRIMARY KEY AUTOINCREMENT,
    record_code         VARCHAR(10) NOT NULL UNIQUE, -- R001

    visit_date          DATE NOT NULL,
    weight_kg           DECIMAL(5,2),
    blood_pressure      VARCHAR(20),

    patient_id          INTEGER NOT NULL,

    FOREIGN KEY (patient_id)
        REFERENCES patient(patient_id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS diagnosis (
    diagnosis_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    diagnosis_code      VARCHAR(10) NOT NULL UNIQUE, -- D001

    diagnosis_name      VARCHAR(100) NOT NULL,
    description         TEXT,
    diagnosed_date      DATE NOT NULL,

    record_id           INTEGER NOT NULL,

    FOREIGN KEY (record_id)
        REFERENCES visit_record(record_id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS prescription (
    prescription_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    prescription_code   VARCHAR(10) NOT NULL UNIQUE, -- RX001

    medication_name     VARCHAR(100) NOT NULL,
    dosage              VARCHAR(50) NOT NULL,

    prescribed_date     DATE NOT NULL,
    prescribed_by       VARCHAR(100) NOT NULL,

    record_id           INTEGER NOT NULL,

    FOREIGN KEY (record_id)
        REFERENCES visit_record(record_id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS document (
    doc_id              INTEGER PRIMARY KEY AUTOINCREMENT,
    doc_code            VARCHAR(10) NOT NULL UNIQUE, -- DOC001

    doc_filename        VARCHAR(200) NOT NULL,
    date_uploaded       DATE NOT NULL,

    vaccine_id          INTEGER,
    record_id           INTEGER,
    diagnosis_id        INTEGER,
    prescription_id     INTEGER,

    FOREIGN KEY (vaccine_id)
        REFERENCES vaccination_shots(vaccine_id)
        ON DELETE CASCADE,

    FOREIGN KEY (record_id)
        REFERENCES visit_record(record_id)
        ON DELETE CASCADE,

    FOREIGN KEY (diagnosis_id)
        REFERENCES diagnosis(diagnosis_id)
        ON DELETE CASCADE,

    FOREIGN KEY (prescription_id)
        REFERENCES prescription(prescription_id)
        ON DELETE CASCADE,

    CHECK (
        (
            CASE WHEN vaccine_id IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN record_id IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN diagnosis_id IS NOT NULL THEN 1 ELSE 0 END +
            CASE WHEN prescription_id IS NOT NULL THEN 1 ELSE 0 END
        ) = 1
    )
);
