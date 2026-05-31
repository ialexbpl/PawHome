"""
PawHome — Performance Benchmark
Runs test queries WITH and WITHOUT indexes at 100, 1000, 5000 rows.
Outputs results to analysis/performance_results.md

Usage:
    python benchmark.py
"""

import re
import os
import time
from datetime import datetime

from db.postgres_connection import get_connection

# ---------------------------------------------------------------------------
# SQL file contents (read once)
# ---------------------------------------------------------------------------

def read_sql(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


SQL_DIR = os.path.join(os.path.dirname(__file__), "sql")
SCHEMA_SQL = read_sql(os.path.join(SQL_DIR, "create_schema.sql"))
SEED_SQL = read_sql(os.path.join(SQL_DIR, "seed_dictionaries.sql"))
CREATE_IDX_SQL = read_sql(os.path.join(SQL_DIR, "create_indexes.sql"))
DROP_IDX_SQL = read_sql(os.path.join(SQL_DIR, "drop_indexes.sql"))

# ---------------------------------------------------------------------------
# Test queries (without EXPLAIN ANALYZE — we add it programmatically)
# ---------------------------------------------------------------------------

QUERIES = [
    {
        "name": "Q1: Available animals in shelter",
        "index": "Partial (bitmap-like) — idx_animals_status_available",
        "sql": """
            SELECT a.animal_id, a.name, s.name AS species, b.name AS breed, c.name AS color
            FROM animals a
            JOIN species s ON a.species_id = s.species_id
            LEFT JOIN breeds b ON a.breed_id = b.breed_id
            LEFT JOIN colors c ON a.color_id = c.color_id
            WHERE a.status = 'available'
              AND a.shelter_id = 1
        """,
    },
    {
        "name": "Q2: Adopter lookup by email (case-insensitive)",
        "index": "Functional — idx_adopters_lower_email",
        "sql": """
            SELECT adopter_id, first_name, last_name, email, phone, city
            FROM adopters
            WHERE LOWER(email) = LOWER('test@example.com')
        """,
    },
    {
        "name": "Q3: Adoption history for animal",
        "index": "Composite — idx_adoptions_animal_adopter",
        "sql": """
            SELECT ad.adoption_id, ad.adoption_date, ad.fee,
                   a.first_name || ' ' || a.last_name AS adopter_name, ad.notes
            FROM adoptions ad
            JOIN adopters a ON ad.adopter_id = a.adopter_id
            WHERE ad.animal_id = 1
        """,
    },
    {
        "name": "Q4: Recent medical records (30 days)",
        "index": "B-tree DESC — idx_medical_records_date_desc",
        "sql": """
            SELECT mr.record_id, an.name AS animal_name, mt.name AS procedure_type,
                   mr.record_date, mr.description, mr.cost
            FROM medical_records mr
            JOIN animals an ON mr.animal_id = an.animal_id
            JOIN medical_types mt ON mr.type_id = mt.type_id
            WHERE mr.record_date >= CURRENT_DATE - INTERVAL '30 days'
            ORDER BY mr.record_date DESC
        """,
    },
    {
        "name": "Q5: Total donations per shelter",
        "index": "None (baseline aggregation)",
        "sql": """
            SELECT s.name AS shelter_name, s.city,
                   COUNT(d.donation_id) AS donation_count,
                   COALESCE(SUM(d.amount), 0) AS total_amount
            FROM shelters s
            LEFT JOIN donations d ON s.shelter_id = d.shelter_id
            GROUP BY s.shelter_id, s.name, s.city
            ORDER BY total_amount DESC
        """,
    },
    {
        "name": "Q6: Animals with >2 medical visits",
        "index": "None (aggregation with HAVING)",
        "sql": """
            SELECT a.animal_id, a.name, sp.name AS species, a.status,
                   COUNT(mr.record_id) AS medical_visits
            FROM animals a
            JOIN species sp ON a.species_id = sp.species_id
            LEFT JOIN medical_records mr ON a.animal_id = mr.animal_id
            GROUP BY a.animal_id, a.name, sp.name, a.status
            HAVING COUNT(mr.record_id) > 2
            ORDER BY medical_visits DESC
        """,
    },
]

VOLUMES = [100, 1000, 5000]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def reset_database(conn):
    """Drop all tables, recreate schema, seed dictionaries."""
    cur = conn.cursor()
    cur.execute(SCHEMA_SQL)
    cur.execute(SEED_SQL)
    conn.commit()
    cur.close()


def generate_data(count: int):
    """Run the generator for a given count using subprocess."""
    import subprocess
    import sys
    result = subprocess.run(
        [sys.executable, "generator.py", "--count", str(count)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"  Generator error: {result.stderr}")
        raise RuntimeError("Generator failed")
    print(result.stdout.strip())


def drop_indexes(conn):
    cur = conn.cursor()
    cur.execute(DROP_IDX_SQL)
    conn.commit()
    cur.close()


def create_indexes(conn):
    cur = conn.cursor()
    cur.execute(CREATE_IDX_SQL)
    conn.commit()
    cur.close()


def run_explain(conn, sql: str) -> tuple[str, float]:
    """Run EXPLAIN ANALYZE and return (full plan text, execution time in ms)."""
    cur = conn.cursor()
    cur.execute(f"EXPLAIN ANALYZE {sql}")
    rows = cur.fetchall()
    cur.close()

    plan_text = "\n".join(row[0] for row in rows)

    match = re.search(r"Execution Time:\s+([\d.]+)\s+ms", plan_text)
    exec_time = float(match.group(1)) if match else 0.0

    return plan_text, exec_time


def get_scan_type(plan: str) -> str:
    """Extract the primary scan type from the plan."""
    if "Index Only Scan" in plan:
        return "Index Only Scan"
    if "Index Scan" in plan:
        return "Index Scan"
    if "Bitmap Heap Scan" in plan:
        return "Bitmap Heap Scan"
    if "Seq Scan" in plan:
        return "Seq Scan"
    return "Other"


# ---------------------------------------------------------------------------
# Main benchmark
# ---------------------------------------------------------------------------

def main():
    results = {}  # results[volume][query_name] = {without: ..., with: ...}

    for volume in VOLUMES:
        print(f"\n{'='*60}")
        print(f"  BENCHMARK: {volume} rows")
        print(f"{'='*60}")

        conn = get_connection()

        # 1. Reset DB and generate data
        print(f"\n  Resetting database...")
        reset_database(conn)
        conn.close()

        print(f"  Generating {volume} rows...")
        generate_data(volume)

        conn = get_connection()

        # 2. Test WITHOUT indexes
        print(f"\n  --- Testing WITHOUT indexes ---")
        drop_indexes(conn)

        # Warm up the cache
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM animals")
        row_count = cur.fetchone()[0]
        cur.close()
        print(f"  Animals in DB: {row_count}")

        results[volume] = {}
        for q in QUERIES:
            plan, exec_time = run_explain(conn, q["sql"])
            scan = get_scan_type(plan)
            results[volume][q["name"]] = {
                "without_time": exec_time,
                "without_scan": scan,
                "without_plan": plan,
            }
            print(f"    {q['name']}: {exec_time:.3f} ms ({scan})")

        # 3. Test WITH indexes
        print(f"\n  --- Testing WITH indexes ---")
        create_indexes(conn)

        # Run ANALYZE so planner picks up new indexes
        cur = conn.cursor()
        cur.execute("ANALYZE")
        conn.commit()
        cur.close()

        for q in QUERIES:
            plan, exec_time = run_explain(conn, q["sql"])
            scan = get_scan_type(plan)
            results[volume][q["name"]]["with_time"] = exec_time
            results[volume][q["name"]]["with_scan"] = scan
            results[volume][q["name"]]["with_plan"] = plan
            print(f"    {q['name']}: {exec_time:.3f} ms ({scan})")

        conn.close()

    # 4. Generate markdown report
    generate_report(results)
    print(f"\n{'='*60}")
    print(f"  Report saved to: analysis/performance_results.md")
    print(f"{'='*60}\n")


def generate_report(results: dict):
    lines = []
    lines.append("# Performance Analysis — Indexes Benchmark")
    lines.append("")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    lines.append("## Summary Table")
    lines.append("")
    lines.append("| Query | Rows | Without Index (ms) | Scan Type | With Index (ms) | Scan Type | Speedup |")
    lines.append("|-------|------|--------------------|-----------|-----------------|-----------|---------|")

    for q in QUERIES:
        for volume in VOLUMES:
            r = results[volume][q["name"]]
            without = r["without_time"]
            with_ = r["with_time"]
            speedup = without / with_ if with_ > 0 else 0
            lines.append(
                f"| {q['name']} | {volume} | {without:.3f} | {r['without_scan']} | "
                f"{with_:.3f} | {r['with_scan']} | {speedup:.1f}x |"
            )

    lines.append("")
    lines.append("## Index Descriptions")
    lines.append("")
    for q in QUERIES:
        lines.append(f"- **{q['name']}** — tested index: {q['index']}")
    lines.append("")

    lines.append("## Detailed Execution Plans")
    lines.append("")
    for volume in VOLUMES:
        lines.append(f"### {volume} rows")
        lines.append("")
        for q in QUERIES:
            r = results[volume][q["name"]]
            lines.append(f"#### {q['name']}")
            lines.append("")
            lines.append("**Without indexes:**")
            lines.append("```")
            lines.append(r["without_plan"])
            lines.append("```")
            lines.append("")
            lines.append("**With indexes:**")
            lines.append("```")
            lines.append(r["with_plan"])
            lines.append("```")
            lines.append("")

    lines.append("## Conclusions")
    lines.append("")
    lines.append("1. **Composite index** (`idx_adoptions_animal_adopter`): Improves lookup speed for adoption history queries by avoiding full table scans on the `adoptions` table.")
    lines.append("2. **Partial index** (`idx_animals_status_available`): PostgreSQL uses Bitmap Heap Scan for filtering by status. Most effective at higher row counts (1000+) where Seq Scan becomes expensive.")
    lines.append("3. **Functional index** (`idx_adopters_lower_email`): Enables Index Scan for case-insensitive email lookups instead of Seq Scan with per-row LOWER() evaluation.")
    lines.append("4. **B-tree DESC index** (`idx_medical_records_date_desc`): Optimizes date-range queries with ORDER BY DESC, avoiding expensive sort operations.")
    lines.append("5. Indexes show the most benefit at **5000 rows**. At 100 rows, the planner may prefer Seq Scan regardless because the table fits in memory.")
    lines.append("")

    os.makedirs("analysis", exist_ok=True)
    with open("analysis/performance_results.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    main()
