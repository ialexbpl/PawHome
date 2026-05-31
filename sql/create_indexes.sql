-- PawHome - Index Definitions
-- 3 required types: composite, bitmap-like (partial), functional
-- + 1 bonus index

-- ============================================================
-- 1. COMPOSITE INDEX (on adoptions)
-- ============================================================
-- Speeds up queries joining/filtering by both animal and adopter,
-- e.g. "find all adoptions for a given animal by a given adopter"
CREATE INDEX idx_adoptions_animal_adopter
    ON adoptions (animal_id, adopter_id);

-- ============================================================
-- 2. PARTIAL INDEX — simulates Bitmap behavior (on animals)
-- ============================================================
-- PostgreSQL doesn't have explicit bitmap indexes like Oracle.
-- Instead, PG automatically uses Bitmap Index Scans when appropriate.
-- This partial index targets only 'available' animals — the most
-- frequently queried status. PG's planner will use a bitmap heap
-- scan with this index on large tables.
CREATE INDEX idx_animals_status_available
    ON animals (status)
    WHERE status = 'available';

-- ============================================================
-- 3. FUNCTIONAL (EXPRESSION) INDEX (on adopters)
-- ============================================================
-- Enables fast case-insensitive email lookups without ILIKE scans.
-- Query: SELECT * FROM adopters WHERE LOWER(email) = 'john@example.com'
CREATE INDEX idx_adopters_lower_email
    ON adopters (LOWER(email));

-- ============================================================
-- 4. BONUS: B-tree index on medical_records date (descending)
-- ============================================================
-- Optimizes queries for recent medical records sorted by date.
CREATE INDEX idx_medical_records_date_desc
    ON medical_records (record_date DESC);
