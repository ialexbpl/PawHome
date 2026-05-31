"""
PawHome — Random Data Generator
Generates random data for 7 key tables in PostgreSQL.
User specifies how many rows to generate. Can be run multiple times
without conflicts (uses DB sequences, randomized unique fields).

Usage:
    python generator.py --count 1000
    python generator.py --count 100
    python generator.py              # defaults to 1000
"""

import argparse
import random
import string
from datetime import date, timedelta

from faker import Faker
from db.postgres_connection import get_connection

fake = Faker()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def random_date(start: date, end: date) -> date:
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, max(delta, 1)))


def random_phone() -> str:
    return f"+1-{random.randint(200,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}"


def unique_email(first: str, last: str, domain: str | None = None) -> str:
    tag = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    domain = domain or random.choice([
        "gmail.com", "yahoo.com", "outlook.com", "mail.com",
    ])
    return f"{first.lower()}.{last.lower()}.{tag}@{domain}"


# ---------------------------------------------------------------------------
# Fetch dictionary IDs already in the database
# ---------------------------------------------------------------------------

def fetch_dict_ids(cur) -> dict:
    ids = {}

    cur.execute("SELECT species_id FROM species")
    ids["species"] = [r[0] for r in cur.fetchall()]

    cur.execute("SELECT breed_id, species_id FROM breeds")
    breeds_raw = cur.fetchall()
    ids["breeds_by_species"] = {}
    for breed_id, species_id in breeds_raw:
        ids["breeds_by_species"].setdefault(species_id, []).append(breed_id)

    cur.execute("SELECT color_id FROM colors")
    ids["colors"] = [r[0] for r in cur.fetchall()]

    cur.execute("SELECT type_id FROM medical_types")
    ids["medical_types"] = [r[0] for r in cur.fetchall()]

    cur.execute("SELECT role_id FROM staff_roles")
    ids["staff_roles"] = [r[0] for r in cur.fetchall()]

    return ids


# ---------------------------------------------------------------------------
# Generators for each key table
# ---------------------------------------------------------------------------

ANIMAL_NAMES = [
    "Buddy", "Max", "Bella", "Charlie", "Luna", "Daisy", "Rocky", "Milo",
    "Coco", "Lucy", "Bear", "Sadie", "Duke", "Molly", "Tucker", "Bailey",
    "Maggie", "Jack", "Lola", "Oliver", "Penny", "Leo", "Rosie", "Finn",
    "Ruby", "Oscar", "Willow", "Zeus", "Chloe", "Toby", "Nala", "Simba",
    "Ginger", "Shadow", "Biscuit", "Pepper", "Hazel", "Scout", "Archie",
    "Stella", "Bruno", "Lily", "Thor", "Ivy", "Rex", "Poppy", "Jasper",
    "Maple", "Ziggy", "Clover",
]

SHELTER_NAMES = [
    "Happy Paws Shelter", "Safe Haven Animal Rescue", "New Beginnings Shelter",
    "Furry Friends Haven", "Second Chance Animal Center", "Paw Prints Rescue",
    "Sunrise Animal Shelter", "Green Valley Pet Refuge", "Bright Tails Shelter",
    "Hope Animal Sanctuary", "Loving Hearts Rescue", "Peaceful Paws Center",
    "Lucky Star Shelter", "Warm Nest Animal Home", "Golden Leash Rescue",
]

DONATION_PURPOSES = [
    "General fund", "Medical care", "Food and supplies", "Shelter renovation",
    "Vaccination program", "Emergency rescue", "Staff training",
    "Community outreach", "Transport vehicle", "Winter heating",
]


def generate_shelters(cur, count: int) -> list[int]:
    n = max(count // 50, 3)  # ~1 shelter per 50 animals, min 3
    ids = []
    for _ in range(n):
        name = random.choice(SHELTER_NAMES) + f" #{random.randint(1, 9999)}"
        cur.execute(
            """INSERT INTO shelters (name, address, city, phone, capacity, opened_date)
               VALUES (%s, %s, %s, %s, %s, %s) RETURNING shelter_id""",
            (
                name,
                fake.street_address(),
                fake.city(),
                random_phone(),
                random.randint(20, 200),
                random_date(date(2000, 1, 1), date(2023, 12, 31)),
            ),
        )
        ids.append(cur.fetchone()[0])
    print(f"  Shelters:        {n} rows inserted")
    return ids


def generate_animals(cur, count: int, shelter_ids: list[int], dicts: dict) -> list[int]:
    ids = []
    for _ in range(count):
        species_id = random.choice(dicts["species"])
        breeds_for_species = dicts["breeds_by_species"].get(species_id, [])
        breed_id = random.choice(breeds_for_species) if breeds_for_species else None
        color_id = random.choice(dicts["colors"]) if dicts["colors"] else None

        cur.execute(
            """INSERT INTO animals
               (name, species_id, breed_id, color_id, date_of_birth, gender,
                weight_kg, shelter_id, intake_date, status)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING animal_id""",
            (
                random.choice(ANIMAL_NAMES),
                species_id,
                breed_id,
                color_id,
                random_date(date(2015, 1, 1), date(2025, 6, 1)),
                random.choice(["M", "F"]),
                round(random.uniform(0.1, 80.0), 2),
                random.choice(shelter_ids),
                random_date(date(2023, 1, 1), date(2026, 3, 1)),
                random.choice(["available", "available", "available", "adopted", "medical_hold"]),
            ),
        )
        ids.append(cur.fetchone()[0])
    print(f"  Animals:         {count} rows inserted")
    return ids


def generate_adopters(cur, count: int) -> list[int]:
    n = max(count // 3, 10)  # ~1 adopter per 3 animals
    ids = []
    for _ in range(n):
        first = fake.first_name()
        last = fake.last_name()
        cur.execute(
            """INSERT INTO adopters
               (first_name, last_name, email, phone, address, city, registered_date)
               VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING adopter_id""",
            (
                first,
                last,
                unique_email(first, last),
                random_phone(),
                fake.street_address(),
                fake.city(),
                random_date(date(2020, 1, 1), date(2026, 3, 1)),
            ),
        )
        ids.append(cur.fetchone()[0])
    print(f"  Adopters:        {n} rows inserted")
    return ids


def generate_staff(cur, count: int, shelter_ids: list[int], dicts: dict) -> list[int]:
    n = max(count // 20, 5)  # ~1 staff per 20 animals
    ids = []
    for _ in range(n):
        first = fake.first_name()
        last = fake.last_name()
        cur.execute(
            """INSERT INTO staff
               (first_name, last_name, role_id, shelter_id, email, phone, hire_date, salary)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s) RETURNING staff_id""",
            (
                first,
                last,
                random.choice(dicts["staff_roles"]),
                random.choice(shelter_ids),
                unique_email(first, last, "pawhome.pl"),
                random_phone(),
                random_date(date(2015, 1, 1), date(2026, 1, 1)),
                round(random.uniform(2000, 8000), 2),
            ),
        )
        ids.append(cur.fetchone()[0])
    print(f"  Staff:           {n} rows inserted")
    return ids


def generate_adoptions(cur, count: int, animal_ids: list[int], adopter_ids: list[int]) -> list[int]:
    n = max(count // 5, 5)  # ~20% of animals get adopted
    adopted_animals = random.sample(animal_ids, min(n, len(animal_ids)))
    ids = []
    for animal_id in adopted_animals:
        cur.execute(
            """INSERT INTO adoptions (animal_id, adopter_id, adoption_date, fee, notes)
               VALUES (%s,%s,%s,%s,%s) RETURNING adoption_id""",
            (
                animal_id,
                random.choice(adopter_ids),
                random_date(date(2023, 6, 1), date(2026, 3, 1)),
                round(random.uniform(25, 500), 2),
                random.choice([None, fake.sentence(), fake.sentence()]),
            ),
        )
        ids.append(cur.fetchone()[0])

        cur.execute(
            "UPDATE animals SET status = 'adopted' WHERE animal_id = %s",
            (animal_id,),
        )
    print(f"  Adoptions:       {len(adopted_animals)} rows inserted")
    return ids


def generate_medical_records(cur, count: int, animal_ids: list[int],
                             staff_ids: list[int], dicts: dict) -> None:
    n = max(count, len(animal_ids))  # at least 1 record per animal on average
    for _ in range(n):
        cur.execute(
            """INSERT INTO medical_records
               (animal_id, type_id, staff_id, record_date, description, cost)
               VALUES (%s,%s,%s,%s,%s,%s)""",
            (
                random.choice(animal_ids),
                random.choice(dicts["medical_types"]),
                random.choice(staff_ids) if staff_ids else None,
                random_date(date(2023, 1, 1), date(2026, 3, 1)),
                fake.sentence(nb_words=8),
                round(random.uniform(10, 1500), 2),
            ),
        )
    print(f"  Medical records: {n} rows inserted")


def generate_donations(cur, count: int, adopter_ids: list[int],
                       shelter_ids: list[int]) -> None:
    n = max(count // 4, 5)
    for _ in range(n):
        cur.execute(
            """INSERT INTO donations
               (adopter_id, shelter_id, amount, donation_date, purpose)
               VALUES (%s,%s,%s,%s,%s)""",
            (
                random.choice(adopter_ids) if random.random() > 0.2 else None,
                random.choice(shelter_ids),
                round(random.uniform(5, 5000), 2),
                random_date(date(2023, 1, 1), date(2026, 3, 1)),
                random.choice(DONATION_PURPOSES),
            ),
        )
    print(f"  Donations:       {n} rows inserted")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="PawHome — random data generator")
    parser.add_argument(
        "--count", type=int, default=1000,
        help="Number of animals to generate (other tables scale proportionally). Default: 1000",
    )
    args = parser.parse_args()
    count = args.count

    print(f"\n=== PawHome Data Generator ===")
    print(f"Generating data for {count} animals (other tables scale proportionally)...\n")

    conn = get_connection()
    try:
        cur = conn.cursor()
        dicts = fetch_dict_ids(cur)

        if not dicts["species"]:
            print("ERROR: Dictionary tables are empty. Run seed_dictionaries.sql first.")
            return

        shelter_ids = generate_shelters(cur, count)
        animal_ids = generate_animals(cur, count, shelter_ids, dicts)
        adopter_ids = generate_adopters(cur, count)
        staff_ids = generate_staff(cur, count, shelter_ids, dicts)
        generate_adoptions(cur, count, animal_ids, adopter_ids)
        generate_medical_records(cur, count, animal_ids, staff_ids, dicts)
        generate_donations(cur, count, adopter_ids, shelter_ids)

        conn.commit()
        print(f"\nDone! All data committed to database.\n")
    except Exception as e:
        conn.rollback()
        print(f"\nERROR: {e}")
        print("Transaction rolled back. No data was inserted.\n")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
