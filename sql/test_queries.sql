-- PawHome - Performance Test Queries
-- Run each with EXPLAIN ANALYZE to compare execution with/without indexes
-- Test at 100, 1000, and 5000 rows

-- ============================================================
-- Query 1: Find all available animals in a specific shelter
-- Tests: partial index (idx_animals_status_available)
-- ============================================================
EXPLAIN ANALYZE
SELECT a.animal_id, a.name, s.name AS species, b.name AS breed, c.name AS color
FROM animals a
JOIN species s ON a.species_id = s.species_id
LEFT JOIN breeds b ON a.breed_id = b.breed_id
LEFT JOIN colors c ON a.color_id = c.color_id
WHERE a.status = 'available'
  AND a.shelter_id = 1;

-- ============================================================
-- Query 2: Look up an adopter by email (case-insensitive)
-- Tests: functional index (idx_adopters_lower_email)
-- ============================================================
EXPLAIN ANALYZE
SELECT adopter_id, first_name, last_name, email, phone, city
FROM adopters
WHERE LOWER(email) = LOWER('test@example.com');

-- ============================================================
-- Query 3: Get full adoption history for a specific animal
-- Tests: composite index (idx_adoptions_animal_adopter)
-- ============================================================
EXPLAIN ANALYZE
SELECT ad.adoption_id, ad.adoption_date, ad.fee,
       a.first_name || ' ' || a.last_name AS adopter_name, ad.notes
FROM adoptions ad
JOIN adopters a ON ad.adopter_id = a.adopter_id
WHERE ad.animal_id = 1;

-- ============================================================
-- Query 4: Recent medical records (last 30 days)
-- Tests: B-tree desc index (idx_medical_records_date_desc)
-- ============================================================
EXPLAIN ANALYZE
SELECT mr.record_id, an.name AS animal_name, mt.name AS procedure_type,
       mr.record_date, mr.description, mr.cost
FROM medical_records mr
JOIN animals an ON mr.animal_id = an.animal_id
JOIN medical_types mt ON mr.type_id = mt.type_id
WHERE mr.record_date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY mr.record_date DESC;

-- ============================================================
-- Query 5: Total donations per shelter (aggregation)
-- ============================================================
EXPLAIN ANALYZE
SELECT s.name AS shelter_name, s.city,
       COUNT(d.donation_id) AS donation_count,
       COALESCE(SUM(d.amount), 0) AS total_amount
FROM shelters s
LEFT JOIN donations d ON s.shelter_id = d.shelter_id
GROUP BY s.shelter_id, s.name, s.city
ORDER BY total_amount DESC;

-- ============================================================
-- Query 6: Animals with their medical record count
-- ============================================================
EXPLAIN ANALYZE
SELECT a.animal_id, a.name, sp.name AS species, a.status,
       COUNT(mr.record_id) AS medical_visits
FROM animals a
JOIN species sp ON a.species_id = sp.species_id
LEFT JOIN medical_records mr ON a.animal_id = mr.animal_id
GROUP BY a.animal_id, a.name, sp.name, a.status
HAVING COUNT(mr.record_id) > 2
ORDER BY medical_visits DESC;
