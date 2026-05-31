-- PawHome - Pet Adoption Center Management System
-- PostgreSQL Schema Definition
-- 12 tables: 5 dictionary + 7 key tables

-- ============================================================
-- Drop tables in reverse dependency order (for re-runs)
-- ============================================================
DROP TABLE IF EXISTS donations       CASCADE;
DROP TABLE IF EXISTS medical_records CASCADE;
DROP TABLE IF EXISTS adoptions       CASCADE;
DROP TABLE IF EXISTS animals         CASCADE;
DROP TABLE IF EXISTS staff           CASCADE;
DROP TABLE IF EXISTS adopters        CASCADE;
DROP TABLE IF EXISTS shelters        CASCADE;
DROP TABLE IF EXISTS breeds          CASCADE;
DROP TABLE IF EXISTS species         CASCADE;
DROP TABLE IF EXISTS colors          CASCADE;
DROP TABLE IF EXISTS medical_types   CASCADE;
DROP TABLE IF EXISTS staff_roles     CASCADE;

-- ============================================================
-- DICTIONARY TABLES
-- ============================================================

CREATE TABLE species (
    species_id  SERIAL       PRIMARY KEY,
    name        VARCHAR(50)  NOT NULL UNIQUE
);

CREATE TABLE breeds (
    breed_id    SERIAL        PRIMARY KEY,
    species_id  INT           NOT NULL REFERENCES species(species_id) ON DELETE CASCADE,
    name        VARCHAR(100)  NOT NULL,
    UNIQUE (species_id, name)
);

CREATE TABLE colors (
    color_id  SERIAL       PRIMARY KEY,
    name      VARCHAR(50)  NOT NULL UNIQUE
);

CREATE TABLE medical_types (
    type_id  SERIAL        PRIMARY KEY,
    name     VARCHAR(100)  NOT NULL UNIQUE
);

CREATE TABLE staff_roles (
    role_id  SERIAL       PRIMARY KEY,
    name     VARCHAR(50)  NOT NULL UNIQUE
);

-- ============================================================
-- KEY TABLES
-- ============================================================

CREATE TABLE shelters (
    shelter_id   SERIAL        PRIMARY KEY,
    name         VARCHAR(100)  NOT NULL,
    address      VARCHAR(255)  NOT NULL,
    city         VARCHAR(100)  NOT NULL,
    phone        VARCHAR(20),
    capacity     INT           NOT NULL CHECK (capacity > 0),
    opened_date  DATE          NOT NULL
);

CREATE TABLE animals (
    animal_id     SERIAL        PRIMARY KEY,
    name          VARCHAR(100)  NOT NULL,
    species_id    INT           NOT NULL REFERENCES species(species_id),
    breed_id      INT           REFERENCES breeds(breed_id),
    color_id      INT           REFERENCES colors(color_id),
    date_of_birth DATE,
    gender        CHAR(1)       CHECK (gender IN ('M', 'F')),
    weight_kg     DECIMAL(5,2),
    shelter_id    INT           NOT NULL REFERENCES shelters(shelter_id),
    intake_date   DATE          NOT NULL,
    status        VARCHAR(20)   NOT NULL DEFAULT 'available'
                                CHECK (status IN ('available', 'adopted', 'medical_hold'))
);

CREATE TABLE adopters (
    adopter_id      SERIAL        PRIMARY KEY,
    first_name      VARCHAR(50)   NOT NULL,
    last_name       VARCHAR(50)   NOT NULL,
    email           VARCHAR(100)  UNIQUE,
    phone           VARCHAR(20),
    address         VARCHAR(255),
    city            VARCHAR(100),
    registered_date DATE          NOT NULL
);

CREATE TABLE adoptions (
    adoption_id    SERIAL        PRIMARY KEY,
    animal_id      INT           NOT NULL REFERENCES animals(animal_id),
    adopter_id     INT           NOT NULL REFERENCES adopters(adopter_id),
    adoption_date  DATE          NOT NULL,
    fee            DECIMAL(8,2)  NOT NULL CHECK (fee >= 0),
    notes          TEXT
);

CREATE TABLE staff (
    staff_id    SERIAL        PRIMARY KEY,
    first_name  VARCHAR(50)   NOT NULL,
    last_name   VARCHAR(50)   NOT NULL,
    role_id     INT           NOT NULL REFERENCES staff_roles(role_id),
    shelter_id  INT           NOT NULL REFERENCES shelters(shelter_id),
    email       VARCHAR(100)  UNIQUE,
    phone       VARCHAR(20),
    hire_date   DATE          NOT NULL,
    salary      DECIMAL(10,2)
);

CREATE TABLE medical_records (
    record_id    SERIAL        PRIMARY KEY,
    animal_id    INT           NOT NULL REFERENCES animals(animal_id),
    type_id      INT           NOT NULL REFERENCES medical_types(type_id),
    staff_id     INT           REFERENCES staff(staff_id),
    record_date  DATE          NOT NULL,
    description  TEXT,
    cost         DECIMAL(8,2)  CHECK (cost >= 0)
);

CREATE TABLE donations (
    donation_id    SERIAL        PRIMARY KEY,
    adopter_id     INT           REFERENCES adopters(adopter_id),
    shelter_id     INT           NOT NULL REFERENCES shelters(shelter_id),
    amount         DECIMAL(10,2) NOT NULL CHECK (amount > 0),
    donation_date  DATE          NOT NULL,
    purpose        VARCHAR(200)
);
