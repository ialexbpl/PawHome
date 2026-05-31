# PawHome — CI/CD + Kubernetes Deployed Pet Adoption App

PawHome is a Flask + PostgreSQL application designed to be deployed through a GitOps workflow on a Kubernetes cluster (k3s compatible) using Argo CD. This repository now prioritizes CI/CD deployment readiness while keeping the original database course implementation and analysis modules.

---

## Table of Contents

- [Deployment First (CI/CD + Argo CD)](#deployment-first-cicd--argo-cd)
- [Release Workflow (GitOps)](#release-workflow-gitops)
- [Project Overview](#project-overview)
- [Tech Stack](#tech-stack)
- [Kubernetes Deployment (k3s + Argo CD Ready)](#kubernetes-deployment-k3s--argo-cd-ready)
- [Database Schema (Relational)](#database-schema-relational)
  - [Tables Overview](#tables-overview)
  - [Schema Diagram](#schema-diagram)
- [Data Generator](#data-generator)
- [Indexes](#indexes)
- [Performance Analysis](#performance-analysis)
- [Data Export / Import (XML & JSON)](#data-export--import-xml--json)
- [GUI Application](#gui-application)
- [Local Setup (Non-Kubernetes)](#local-setup-non-kubernetes)
- [Project Structure](#project-structure)

---

## Deployment First (CI/CD + Argo CD)

This project is structured for cluster-first delivery:

- Kubernetes manifests live in `k8s/` and are rendered via `k8s/kustomization.yaml`.
- Argo CD application manifest lives in `argocd/pawhome-application.yaml`.
- PostgreSQL, application deployment, DB secret, and DB bootstrap SQL are all declarative manifests.
- Cluster target is standard Kubernetes API and works on Ubuntu k3s.

### Deploy in 5 steps

1. Build and push your app image.
2. Update image tag in `k8s/app.yaml`.
3. Set DB password in `k8s/postgres-secret.yaml`.
4. Set Git repo URL in `argocd/pawhome-application.yaml`.
5. Apply Argo application once:

```bash
kubectl apply -f argocd/pawhome-application.yaml -n argocd
```

After that, Argo CD tracks this repo and reconciles changes automatically.

---

## Release Workflow (GitOps)

| Step | Action | Trigger |
|---|---|---|
| 1 | Commit and push code/manifests | Developer push |
| 2 | Build and push Docker image with new tag | CI pipeline or local build |
| 3 | Update `k8s/app.yaml` image tag and push | Git change |
| 4 | Argo CD detects Git change and syncs cluster | Auto-sync |
| 5 | Verify pods/services/PVC and app health | Post-deploy checks |

Recommended command checks:

```bash
kubectl -n pawhome get pods,svc,pvc
kubectl -n pawhome logs deployment/pawhome-web
kubectl -n pawhome logs statefulset/pawhome-postgres
```

---

## Project Overview

**PawHome** is a management system for a pet adoption center. It tracks:

- Animals available for adoption (dogs, cats, rabbits, etc.)
- Breeds and species information
- Shelter locations and capacity
- Adopters and their contact details
- Adoption records and history
- Medical records and vaccinations
- Staff members and their roles
- Donations and sponsors

The system allows center employees to register new animals, manage adoptions, track medical history, and generate reports — all through a web-based graphical interface.

---

## Tech Stack

| Layer              | Technology                |
| ------------------ | ------------------------- |
| Relational DB      | PostgreSQL 16+ (e.g. 18)  |
| Backend            | Python 3.13+ / Flask      |
| Frontend           | Jinja2 templates + Bootstrap 5 |
| Data Generator     | Python + Faker            |
| Export/Import      | JSON and XML (built into Flask app) |
| Performance Tools  | EXPLAIN ANALYZE (PostgreSQL) |

---

## Database Schema (Relational)

### Tables Overview

The relational database consists of **12 tables** — 5 dictionary (lookup) tables and 7 key (data) tables.

#### Dictionary Tables (lookup/reference data)

| # | Table            | Description                                       |
|---|------------------|---------------------------------------------------|
| 1 | `species`        | Animal species (Dog, Cat, Rabbit, Bird, etc.)     |
| 2 | `breeds`         | Breeds per species (Labrador, Siamese, etc.)      |
| 3 | `colors`         | Possible animal coat/fur colors                   |
| 4 | `medical_types`  | Types of medical procedures (vaccine, surgery, checkup) |
| 5 | `staff_roles`    | Staff position types (vet, caretaker, admin, volunteer) |

#### Key Tables (operational data)

| # | Table            | Description                                                     |
|---|------------------|-----------------------------------------------------------------|
| 6 | `shelters`       | Shelter locations (name, address, capacity, phone)              |
| 7 | `animals`        | Animals in the system (name, age, species, breed, color, status)|
| 8 | `adopters`       | People who adopt animals (name, email, phone, address)          |
| 9 | `adoptions`      | Adoption events linking an animal to an adopter                 |
|10 | `medical_records`| Medical history per animal (procedure, date, vet, notes)        |
|11 | `staff`          | Employees and volunteers (name, role, shelter, hire date)       |
|12 | `donations`      | Financial donations (adopter/donor, amount, date, purpose)      |

### Column Details

#### `species`
| Column       | Type         | Constraints       | Description              |
|--------------|--------------|--------------------|--------------------------|
| species_id   | SERIAL       | PK                 | Unique species identifier|
| name         | VARCHAR(50)  | NOT NULL, UNIQUE   | Species name             |

#### `breeds`
| Column       | Type         | Constraints              | Description              |
|--------------|--------------|--------------------------|--------------------------|
| breed_id     | SERIAL       | PK                       | Unique breed identifier  |
| species_id   | INT          | FK → species, NOT NULL   | Parent species           |
| name         | VARCHAR(100) | NOT NULL                 | Breed name               |

#### `colors`
| Column       | Type         | Constraints       | Description              |
|--------------|--------------|--------------------|--------------------------|
| color_id     | SERIAL       | PK                 | Unique color identifier  |
| name         | VARCHAR(50)  | NOT NULL, UNIQUE   | Color name               |

#### `medical_types`
| Column       | Type         | Constraints       | Description              |
|--------------|--------------|--------------------|--------------------------|
| type_id      | SERIAL       | PK                 | Unique type identifier   |
| name         | VARCHAR(100) | NOT NULL, UNIQUE   | Procedure type name      |

#### `staff_roles`
| Column       | Type         | Constraints       | Description              |
|--------------|--------------|--------------------|--------------------------|
| role_id      | SERIAL       | PK                 | Unique role identifier   |
| name         | VARCHAR(50)  | NOT NULL, UNIQUE   | Role title               |

#### `shelters`
| Column       | Type          | Constraints       | Description              |
|--------------|---------------|--------------------|--------------------------|
| shelter_id   | SERIAL        | PK                 | Unique shelter identifier|
| name         | VARCHAR(100)  | NOT NULL           | Shelter name             |
| address      | VARCHAR(255)  | NOT NULL           | Full address             |
| city         | VARCHAR(100)  | NOT NULL           | City                     |
| phone        | VARCHAR(20)   |                    | Contact phone            |
| capacity     | INT           | NOT NULL, CHECK>0  | Max animal capacity      |
| opened_date  | DATE          | NOT NULL           | Date shelter opened      |

#### `animals`
| Column       | Type          | Constraints                | Description                |
|--------------|---------------|----------------------------|----------------------------|
| animal_id    | SERIAL        | PK                         | Unique animal identifier   |
| name         | VARCHAR(100)  | NOT NULL                   | Animal's name              |
| species_id   | INT           | FK → species, NOT NULL     | Species                    |
| breed_id     | INT           | FK → breeds                | Breed (nullable for mixed) |
| color_id     | INT           | FK → colors                | Primary color              |
| date_of_birth| DATE          |                            | Estimated birth date       |
| gender       | CHAR(1)       | CHECK IN ('M','F')         | M or F                     |
| weight_kg    | DECIMAL(5,2)  |                            | Weight in kilograms        |
| shelter_id   | INT           | FK → shelters, NOT NULL    | Current shelter            |
| intake_date  | DATE          | NOT NULL                   | Date entered the shelter   |
| status       | VARCHAR(20)   | NOT NULL, DEFAULT 'available' | available / adopted / medical_hold |

#### `adopters`
| Column       | Type          | Constraints       | Description              |
|--------------|---------------|--------------------|--------------------------|
| adopter_id   | SERIAL        | PK                 | Unique adopter identifier|
| first_name   | VARCHAR(50)   | NOT NULL           | First name               |
| last_name    | VARCHAR(50)   | NOT NULL           | Last name                |
| email        | VARCHAR(100)  | UNIQUE             | Email address            |
| phone        | VARCHAR(20)   |                    | Phone number             |
| address      | VARCHAR(255)  |                    | Home address             |
| city         | VARCHAR(100)  |                    | City                     |
| registered_date | DATE       | NOT NULL           | Registration date        |

#### `adoptions`
| Column        | Type         | Constraints                   | Description                 |
|---------------|--------------|-------------------------------|-----------------------------|
| adoption_id   | SERIAL       | PK                            | Unique adoption identifier  |
| animal_id     | INT          | FK → animals, NOT NULL        | Adopted animal              |
| adopter_id    | INT          | FK → adopters, NOT NULL       | Person who adopted          |
| adoption_date | DATE         | NOT NULL                      | Date of adoption            |
| fee           | DECIMAL(8,2) | NOT NULL, CHECK >= 0          | Adoption fee paid           |
| notes         | TEXT         |                               | Additional notes            |

#### `medical_records`
| Column        | Type          | Constraints                   | Description                 |
|---------------|---------------|-------------------------------|-----------------------------|
| record_id     | SERIAL        | PK                            | Unique record identifier    |
| animal_id     | INT           | FK → animals, NOT NULL        | Animal treated              |
| type_id       | INT           | FK → medical_types, NOT NULL  | Type of procedure           |
| staff_id      | INT           | FK → staff                    | Vet / staff who performed   |
| record_date   | DATE          | NOT NULL                      | Date of procedure           |
| description   | TEXT          |                               | Procedure details           |
| cost          | DECIMAL(8,2)  | CHECK >= 0                    | Cost of procedure           |

#### `staff`
| Column        | Type          | Constraints                   | Description                 |
|---------------|---------------|-------------------------------|-----------------------------|
| staff_id      | SERIAL        | PK                            | Unique staff identifier     |
| first_name    | VARCHAR(50)   | NOT NULL                      | First name                  |
| last_name     | VARCHAR(50)   | NOT NULL                      | Last name                   |
| role_id       | INT           | FK → staff_roles, NOT NULL    | Job role                    |
| shelter_id    | INT           | FK → shelters, NOT NULL       | Assigned shelter            |
| email         | VARCHAR(100)  | UNIQUE                        | Work email                  |
| phone         | VARCHAR(20)   |                               | Phone number                |
| hire_date     | DATE          | NOT NULL                      | Employment start date       |
| salary        | DECIMAL(10,2) |                               | Monthly salary              |

#### `donations`
| Column         | Type          | Constraints                   | Description                 |
|----------------|---------------|-------------------------------|-----------------------------|
| donation_id    | SERIAL        | PK                            | Unique donation identifier  |
| adopter_id     | INT           | FK → adopters                 | Donor (nullable for anon.)  |
| shelter_id     | INT           | FK → shelters, NOT NULL       | Receiving shelter           |
| amount         | DECIMAL(10,2) | NOT NULL, CHECK > 0           | Donation amount             |
| donation_date  | DATE          | NOT NULL                      | Date of donation            |
| purpose        | VARCHAR(200)  |                               | What the donation is for    |

### Schema Diagram

```
┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│   species     │──1:N──│    breeds     │       │    colors     │
│──────────────│       │──────────────│       │──────────────│
│ species_id PK│       │ breed_id   PK│       │ color_id   PK│
│ name         │       │ species_id FK│       │ name         │
└──────┬───────┘       └──────┬───────┘       └──────┬───────┘
       │                      │                      │
       └──────────┬───────────┘                      │
                  │                                   │
            ┌─────▼─────────────────────────────────▼──┐
            │              animals                      │
            │──────────────────────────────────────────│
            │ animal_id PK    │ species_id FK           │
            │ name            │ breed_id   FK           │
            │ date_of_birth   │ color_id   FK           │
            │ gender, weight  │ shelter_id FK           │
            │ intake_date     │ status                  │
            └──┬──────────────┬─────────────────┬──────┘
               │              │                 │
    ┌──────────▼──┐   ┌──────▼───────┐   ┌─────▼──────────┐
    │  adoptions   │   │medical_records│   │   shelters      │
    │─────────────│   │──────────────│   │────────────────│
    │adoption_id PK│   │ record_id  PK│   │ shelter_id  PK │
    │ animal_id FK │   │ animal_id  FK│   │ name, address  │
    │ adopter_id FK│   │ type_id    FK│──→│ city, capacity │
    │ adoption_date│   │ staff_id   FK│   └──┬──────┬──────┘
    │ fee, notes   │   │ record_date  │      │      │
    └──────┬──────┘   │ description  │      │      │
           │          │ cost         │      │      │
    ┌──────▼──────┐   └──────────────┘      │      │
    │  adopters    │                    ┌────▼──┐ ┌─▼────────┐
    │─────────────│                    │ staff  │ │donations  │
    │adopter_id PK│                    │───────│ │──────────│
    │ first_name   │                    │staff_id│ │donation_id│
    │ last_name    │                    │role_id │ │adopter_id │
    │ email, phone │                    │shelter │ │shelter_id │
    │ address,city │                    │hire_dt │ │amount     │
    │ registered   │                    │salary  │ │date       │
    └─────────────┘                    └───┬───┘ └───────────┘
                                           │
                                           │    ┌──────────────┐
                                           └────│ staff_roles   │
           ┌──────────────┐                     │──────────────│
           │ medical_types │                     │ role_id    PK│
           │──────────────│                     │ name         │
           │ type_id    PK│                     └──────────────┘
           │ name         │
           └──────────────┘
```

---

## Data Generator

A Python script (`generator.py`) that populates the key tables with random but realistic data using the **Faker** library.

### Features

- User specifies the number of rows to generate (e.g. 10, 100, 1000, 5000)
- Generates data for all 7 key tables: `shelters`, `animals`, `adopters`, `adoptions`, `medical_records`, `staff`, `donations`
- Respects foreign key constraints and referential integrity
- Can be run multiple times — new rows are appended without conflicts (uses database sequences for IDs, unique fields are randomized)
- Dictionary tables are pre-seeded with fixed reference data

### Usage

```bash
python generator.py --count 1000
```

This inserts 1000 animals, proportional numbers of adopters, adoptions, medical records, staff, and donations.

---

## Indexes

Four indexes are created (3 required types + 1 bonus):

### 1. Composite Index (on `adoptions`)

```sql
CREATE INDEX idx_adoptions_animal_adopter
ON adoptions (animal_id, adopter_id);
```

Speeds up queries that filter or join on both the animal and adopter in adoption records.

### 2. Partial Index — simulating Bitmap behavior (on `animals`)

```sql
CREATE INDEX idx_animals_status_available
ON animals (status)
WHERE status = 'available';
```

> **Note:** PostgreSQL does not have explicit bitmap indexes like Oracle. Instead, PostgreSQL automatically uses **Bitmap Index Scans** when appropriate. This partial index targets only available animals, which is the most frequently queried status. PostgreSQL's query planner may use a bitmap heap scan with this index.

Optimizes the most common query: finding animals currently available for adoption.

### 3. Functional (Expression) Index (on `adopters`)

```sql
CREATE INDEX idx_adopters_lower_email
ON adopters (LOWER(email));
```

Allows case-insensitive email lookups without full table scans.

### 4. B-tree DESC Index (on `medical_records`)

```sql
CREATE INDEX idx_medical_records_date_desc
ON medical_records (record_date DESC);
```

Speeds up queries retrieving recent medical records sorted by date.

---

## Performance Analysis

Queries are tested with `EXPLAIN ANALYZE` at three data volumes: **100**, **1000**, and **5000** rows.

An automated benchmark script (`benchmark.py`) handles the full cycle:

1. Resets the database and generates data for each volume
2. Drops indexes → runs 6 test queries → records execution plans and times
3. Creates indexes → runs ANALYZE → runs same queries → records results
4. Generates a markdown report to `analysis/performance_results.md`

### Test Queries

1. **Find all available animals in a specific shelter** — tests partial (bitmap-like) index
2. **Look up an adopter by email (case-insensitive)** — tests functional index
3. **Get adoption history for a specific animal** — tests composite index
4. **Recent medical records in the last 30 days** — tests B-tree DESC index
5. **Total donations per shelter** — aggregation baseline
6. **Animals with >2 medical visits** — aggregation with HAVING

### Usage

```bash
python benchmark.py
```

Results saved to `analysis/performance_results.md` with a summary table (time without/with indexes, scan types, speedup) and full EXPLAIN ANALYZE plans.

---

## Data Export / Import (XML & JSON)

Export and import is built into the Flask web application (Tools page).

### Features

- **Export** all 12 tables to JSON or XML — downloads as a file
- **Import** from JSON or XML — maintains insertion order for referential integrity, skips duplicate rows
- Accessible from the GUI at `http://localhost:5000/tools`

---

## GUI Application

A web application built with **Flask + Jinja2 + Bootstrap 5**, accessible at `http://localhost:5000`.

### Features

- **Dashboard** — overview cards (animals, adopters, adoptions, donations with total amount), top shelters by animal count, recent adoptions
- **Animals** — full CRUD, filter by status and shelter, Bootstrap modals for add/edit
- **Adopters** — full CRUD, shows adoption count per adopter
- **Adoptions** — full CRUD, auto-sets animal status to adopted/available
- **Medical Records** — full CRUD, links to animals, procedure types, and staff
- **Staff** — full CRUD, role and shelter assignment
- **Donations** — full CRUD, optional anonymous donor
- **Tools page**:
  - Data Generator — specify count and run
  - Performance Benchmark — run full analysis
  - Export data to JSON or XML (download)
  - Import data from JSON or XML (upload)

---

## Local Setup (Non-Kubernetes)

Use this section only for local development. For cluster deployments, use the Argo CD flow above.

### Prerequisites

- Python 3.13+
- **PostgreSQL 16+** (works with PostgreSQL 18)

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/your-username/pawhome.git
cd pawhome

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\Activate.ps1       # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure connection
cp .env.example .env
# Edit .env with your database credentials
```

### SQL Execution Order (PostgreSQL)

All SQL scripts are written for **PostgreSQL**. Run them in the following order:

| Step | File | What it does |
|------|------|--------------|
| 1 | `sql/create_schema.sql` | Creates all 12 tables (drops existing ones first). Defines PKs, FKs, CHECK constraints, UNIQUE constraints, DEFAULT values. |
| 2 | `sql/seed_dictionaries.sql` | Populates 5 dictionary tables with reference data (species, breeds, colors, medical types, staff roles). Safe to re-run — uses `ON CONFLICT DO NOTHING`. |
| 3 | *(run generator.py)* | Generate random data for key tables. |
| 4 | `sql/drop_indexes.sql` | Drop custom indexes (before testing queries **without** indexes). |
| 5 | `sql/test_queries.sql` | Run `EXPLAIN ANALYZE` queries — record results **without** indexes. |
| 6 | `sql/create_indexes.sql` | Create 4 indexes: composite, partial (bitmap-like), functional, B-tree DESC. |
| 7 | `sql/test_queries.sql` | Run the same queries again — record results **with** indexes. Compare. |

```bash
# Step 1 — Create tables
psql -U postgres -d pawhome -f sql/create_schema.sql

# Step 2 — Seed dictionary data
psql -U postgres -d pawhome -f sql/seed_dictionaries.sql

# Step 3 — Generate random data (e.g. 1000 rows)
python generator.py --count 1000

# Step 4 — Drop indexes (test WITHOUT indexes first)
psql -U postgres -d pawhome -f sql/drop_indexes.sql

# Step 5 — Run test queries, save results
psql -U postgres -d pawhome -f sql/test_queries.sql

# Step 6 — Create indexes
psql -U postgres -d pawhome -f sql/create_indexes.sql

# Step 7 — Run test queries again, compare results
psql -U postgres -d pawhome -f sql/test_queries.sql
```

> **Note:** For the performance analysis at multiple data volumes (100, 1000, 5000 rows), repeat steps 1–7 for each volume, or simply run `python benchmark.py` which automates the entire process.

### Running the GUI

```bash
python app.py
# Open http://localhost:5000
```

---

## Kubernetes Deployment (k3s + Argo CD Ready)

You can run both the **Flask app** and **PostgreSQL** on Kubernetes, including remote Ubuntu k3s clusters.

### Prerequisites

- Docker (logged in to your image registry)
- `kubectl` connected to your cluster
- A reachable image repository (Docker Hub, GHCR, ACR, etc.)

### 1) Push your app image

```powershell
docker build -t ghcr.io/<your-user>/pawhome:v1 .
docker push ghcr.io/<your-user>/pawhome:v1
```

### 2) Set image and DB password in manifests

- Update `k8s/app.yaml` image from `ghcr.io/replace-me/pawhome:latest` to your pushed image.
- Update `k8s/postgres-secret.yaml` value `POSTGRES_PASSWORD`.

### 3) Deploy with Argo CD

Apply the Argo CD `Application` manifest (after setting your repo URL):

```bash
kubectl apply -f argocd/pawhome-application.yaml -n argocd
```

Argo will sync path `k8s/` using `k8s/kustomization.yaml`.

### 4) Open the app

For quick access:

```bash
kubectl -n pawhome port-forward svc/pawhome-web 5000:5000
```

Then open: `http://localhost:5000`

### Useful checks

```bash
kubectl -n pawhome get pods
kubectl -n pawhome get svc
kubectl -n pawhome get pvc
kubectl -n pawhome logs deployment/pawhome-web
kubectl -n pawhome logs statefulset/pawhome-postgres
```

---

## Project Structure

```
Database-labs/
├── app.py                      # Flask web app — routes, CRUD, tools
├── generator.py                # Random data generator (Python + Faker)
├── benchmark.py                # Automated performance benchmark
├── requirements.txt            # Python dependencies
├── .env.example                # DB connection config template
├── .env                        # DB connection config (not in git)
├── db/
│   └── postgres_connection.py  # psycopg2 connection helper
├── sql/
│   ├── create_schema.sql       # DDL — all 12 tables
│   ├── seed_dictionaries.sql   # Insert dictionary data
│   ├── create_indexes.sql      # 4 index definitions
│   ├── drop_indexes.sql        # Drop custom indexes
│   └── test_queries.sql        # 6 EXPLAIN ANALYZE queries
├── templates/
│   ├── base.html               # Bootstrap 5 layout + sidebar
│   ├── dashboard.html          # Stats overview
│   ├── animals.html            # Animals CRUD
│   ├── adopters.html           # Adopters CRUD
│   ├── adoptions.html          # Adoptions CRUD
│   ├── medical.html            # Medical records CRUD
│   ├── staff.html              # Staff CRUD
│   ├── donations.html          # Donations CRUD
│   └── tools.html              # Generator, benchmark, export/import
└── analysis/                   # Generated by benchmark.py
    └── performance_results.md  # Index analysis results
```

---

## License

This project is created for educational purposes as part of a university Database course.
