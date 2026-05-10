CREATE DATABASE IF NOT EXISTS healthlink;
USE healthlink;

CREATE TABLE patient (
    patient_id      VARCHAR(20) PRIMARY KEY,
    first_name      VARCHAR(50) NOT NULL,
    last_name       VARCHAR(50) NOT NULL,
    birthdate       DATE NOT NULL,
    sex             VARCHAR(10) NOT NULL
);

-- Multivalued contact numbers
CREATE TABLE patient_contact (
    contact_id      BIGINT AUTO_INCREMENT PRIMARY KEY,
    patient_id      VARCHAR(20) NOT NULL,
    contact_number  VARCHAR(20) NOT NULL,

    CONSTRAINT fk_patient_contact_patient
        FOREIGN KEY (patient_id)
        REFERENCES patient(patient_id)
        ON DELETE CASCADE
);

CREATE TABLE vaccination_shots (
    vaccine_id          VARCHAR(20) PRIMARY KEY,
    vaccination_name    VARCHAR(100) NOT NULL,
    date_administered   DATE NOT NULL,
    facility            VARCHAR(100) NOT NULL,
    dose_number         INT NOT NULL,
    schedule_date       DATE NOT NULL,
    status              VARCHAR(20) NOT NULL,
    patient_id          VARCHAR(20) NOT NULL,

    CONSTRAINT fk_vaccine_patient
        FOREIGN KEY (patient_id)
        REFERENCES patient(patient_id)
        ON DELETE CASCADE
);

CREATE TABLE appointment (
    appointment_id  VARCHAR(20) PRIMARY KEY,
    appt_date       DATE NOT NULL,
    appt_time       TIME NOT NULL,
    purpose         VARCHAR(200) NOT NULL,
    clinic_name     VARCHAR(100) NOT NULL,
    status          VARCHAR(20) NOT NULL,
    patient_id      VARCHAR(20) NOT NULL,

    CONSTRAINT fk_appointment_patient
        FOREIGN KEY (patient_id)
        REFERENCES patient(patient_id)
        ON DELETE CASCADE
);

CREATE TABLE visit_record (
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

CREATE TABLE diagnosis (
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

CREATE TABLE prescription (
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

CREATE TABLE document (
    doc_id              VARCHAR(20) PRIMARY KEY,
    doc_filename        VARCHAR(200) NOT NULL,
    date_uploaded       DATE NOT NULL,
    vaccine_id          VARCHAR(20),
    record_id           VARCHAR(20),

    CONSTRAINT fk_document_vaccine
        FOREIGN KEY (vaccine_id)
        REFERENCES vaccination_shots(vaccine_id)
        ON DELETE SET NULL,

    CONSTRAINT fk_document_record
        FOREIGN KEY (record_id)
        REFERENCES visit_record(record_id)
        ON DELETE SET NULL
);


ALTER TABLE patient
ADD CONSTRAINT chk_patient_sex
CHECK (sex IN ('Male', 'Female'));

ALTER TABLE vaccination_shots
ADD CONSTRAINT chk_vaccine_status
CHECK (status IN ('Pending', 'Completed', 'Missed'));

ALTER TABLE appointment
ADD CONSTRAINT chk_appointment_status
CHECK (status IN ('Scheduled', 'Completed', 'Cancelled'));


CREATE INDEX idx_vaccine_patient
ON vaccination_shots(patient_id);

CREATE INDEX idx_appointment_patient
ON appointment(patient_id);

CREATE INDEX idx_visit_patient
ON visit_record(patient_id);

CREATE INDEX idx_diagnosis_record
ON diagnosis(record_id);

CREATE INDEX idx_prescription_record
ON prescription(record_id);

CREATE INDEX idx_document_vaccine
ON document(vaccine_id);

CREATE INDEX idx_document_record
ON document(record_id);
