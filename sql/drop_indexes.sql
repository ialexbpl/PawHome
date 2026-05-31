-- PawHome - Drop Custom Indexes
-- Used before performance testing without indexes

DROP INDEX IF EXISTS idx_adoptions_animal_adopter;
DROP INDEX IF EXISTS idx_animals_status_available;
DROP INDEX IF EXISTS idx_adopters_lower_email;
DROP INDEX IF EXISTS idx_medical_records_date_desc;
