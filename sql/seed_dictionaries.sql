-- PawHome - Seed Dictionary Tables
-- Run after create_schema.sql

-- ============================================================
-- Species
-- ============================================================
INSERT INTO species (name) VALUES
    ('Dog'),
    ('Cat'),
    ('Rabbit'),
    ('Bird'),
    ('Hamster'),
    ('Guinea Pig'),
    ('Turtle'),
    ('Fish')
ON CONFLICT (name) DO NOTHING;

-- ============================================================
-- Breeds (species_id references inserted above)
-- ============================================================

-- Dogs (species_id = 1)
INSERT INTO breeds (species_id, name) VALUES
    (1, 'Labrador Retriever'),
    (1, 'German Shepherd'),
    (1, 'Golden Retriever'),
    (1, 'Bulldog'),
    (1, 'Beagle'),
    (1, 'Poodle'),
    (1, 'Husky'),
    (1, 'Dachshund'),
    (1, 'Boxer'),
    (1, 'Mixed Breed')
ON CONFLICT (species_id, name) DO NOTHING;

-- Cats (species_id = 2)
INSERT INTO breeds (species_id, name) VALUES
    (2, 'Persian'),
    (2, 'Siamese'),
    (2, 'Maine Coon'),
    (2, 'British Shorthair'),
    (2, 'Ragdoll'),
    (2, 'Bengal'),
    (2, 'Sphynx'),
    (2, 'Abyssinian'),
    (2, 'Mixed Breed')
ON CONFLICT (species_id, name) DO NOTHING;

-- Rabbits (species_id = 3)
INSERT INTO breeds (species_id, name) VALUES
    (3, 'Holland Lop'),
    (3, 'Netherland Dwarf'),
    (3, 'Mini Rex'),
    (3, 'Lionhead'),
    (3, 'Flemish Giant'),
    (3, 'Mixed Breed')
ON CONFLICT (species_id, name) DO NOTHING;

-- Birds (species_id = 4)
INSERT INTO breeds (species_id, name) VALUES
    (4, 'Budgerigar'),
    (4, 'Cockatiel'),
    (4, 'Canary'),
    (4, 'Lovebird'),
    (4, 'Finch')
ON CONFLICT (species_id, name) DO NOTHING;

-- Hamsters (species_id = 5)
INSERT INTO breeds (species_id, name) VALUES
    (5, 'Syrian'),
    (5, 'Dwarf Campbell'),
    (5, 'Roborovski'),
    (5, 'Chinese')
ON CONFLICT (species_id, name) DO NOTHING;

-- Guinea Pigs (species_id = 6)
INSERT INTO breeds (species_id, name) VALUES
    (6, 'American'),
    (6, 'Abyssinian'),
    (6, 'Peruvian'),
    (6, 'Teddy')
ON CONFLICT (species_id, name) DO NOTHING;

-- Turtles (species_id = 7)
INSERT INTO breeds (species_id, name) VALUES
    (7, 'Red-Eared Slider'),
    (7, 'Box Turtle'),
    (7, 'Painted Turtle')
ON CONFLICT (species_id, name) DO NOTHING;

-- Fish (species_id = 8)
INSERT INTO breeds (species_id, name) VALUES
    (8, 'Goldfish'),
    (8, 'Betta'),
    (8, 'Guppy'),
    (8, 'Neon Tetra')
ON CONFLICT (species_id, name) DO NOTHING;

-- ============================================================
-- Colors
-- ============================================================
INSERT INTO colors (name) VALUES
    ('Black'),
    ('White'),
    ('Brown'),
    ('Golden'),
    ('Gray'),
    ('Orange'),
    ('Cream'),
    ('Spotted'),
    ('Striped'),
    ('Tricolor'),
    ('Red'),
    ('Blue'),
    ('Silver'),
    ('Tan'),
    ('Brindle')
ON CONFLICT (name) DO NOTHING;

-- ============================================================
-- Medical Types
-- ============================================================
INSERT INTO medical_types (name) VALUES
    ('Vaccination'),
    ('Spay/Neuter'),
    ('General Checkup'),
    ('Dental Cleaning'),
    ('Surgery'),
    ('X-Ray'),
    ('Blood Test'),
    ('Deworming'),
    ('Flea Treatment'),
    ('Microchip Implant'),
    ('Wound Treatment'),
    ('Allergy Treatment')
ON CONFLICT (name) DO NOTHING;

-- ============================================================
-- Staff Roles
-- ============================================================
INSERT INTO staff_roles (name) VALUES
    ('Veterinarian'),
    ('Vet Technician'),
    ('Caretaker'),
    ('Receptionist'),
    ('Manager'),
    ('Volunteer'),
    ('Cleaner'),
    ('Driver')
ON CONFLICT (name) DO NOTHING;
