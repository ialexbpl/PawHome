"""
PawHome — Flask Web Application
CRUD interface for the Pet Adoption Center database.
"""

import json
import os
import subprocess
import sys

from flask import (
    Flask, render_template, request, redirect, url_for, flash, send_file, g,
)

from db.postgres_connection import get_connection

app = Flask(__name__)
app.secret_key = os.urandom(24)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_db():
    if "db_conn" not in g:
        conn = get_connection()
        conn.autocommit = True
        g.db_conn = conn
    return g.db_conn


@app.teardown_appcontext
def close_db(error=None):
    conn = g.pop("db_conn", None)
    if conn is not None:
        conn.close()


def query(sql, params=None, fetchone=False):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(sql, params or ())
    if cur.description is None:
        cur.close()
        return None
    cols = [d[0] for d in cur.description]
    if fetchone:
        row = cur.fetchone()
        rows = [dict(zip(cols, row))] if row else []
    else:
        rows = [dict(zip(cols, row)) for row in cur.fetchall()]
    cur.close()
    return rows[0] if fetchone and rows and rows[0] else rows


def execute(sql, params=None):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(sql, params or ())
    cur.close()


def get_pagination(default_per_page=50, max_per_page=200):
    page = request.args.get("page", 1, type=int) or 1
    per_page = request.args.get("per_page", default_per_page, type=int) or default_per_page
    if page < 1:
        page = 1
    if per_page < 1:
        per_page = default_per_page
    per_page = min(per_page, max_per_page)
    offset = (page - 1) * per_page
    return page, per_page, offset


# Dictionary helpers — used in dropdowns
def get_species():
    return query("SELECT species_id, name FROM species ORDER BY name")

def get_breeds():
    return query("SELECT breed_id, species_id, name FROM breeds ORDER BY name")

def get_colors():
    return query("SELECT color_id, name FROM colors ORDER BY name")

def get_shelters():
    return query("SELECT shelter_id, name, city FROM shelters ORDER BY name")

def get_staff_roles():
    return query("SELECT role_id, name FROM staff_roles ORDER BY name")

def get_medical_types():
    return query("SELECT type_id, name FROM medical_types ORDER BY name")

def get_staff_list():
    return query("SELECT staff_id, first_name || ' ' || last_name AS name FROM staff ORDER BY last_name")

def get_adopters_list():
    return query("SELECT adopter_id, first_name || ' ' || last_name AS name FROM adopters ORDER BY last_name")

def get_animals_list():
    return query("SELECT animal_id, name || ' (#' || animal_id || ')' AS label FROM animals ORDER BY name")


# ---------------------------------------------------------------------------
# Health checks
# ---------------------------------------------------------------------------

@app.route("/healthz/live")
def health_live():
    return {"status": "alive"}, 200


@app.route("/healthz/ready")
def health_ready():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.close()
        return {"status": "ready"}, 200
    except Exception:
        return {"status": "not_ready"}, 503


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

@app.route("/")
def dashboard():
    stats = {}
    tables = ["animals", "adopters", "adoptions", "shelters", "staff", "donations", "medical_records"]
    conn = get_db()
    cur = conn.cursor()
    for t in tables:
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        stats[t] = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM animals WHERE status = 'available'")
    stats["available"] = cur.fetchone()[0]

    cur.execute("SELECT COALESCE(SUM(amount), 0) FROM donations")
    stats["total_donated"] = cur.fetchone()[0]

    cur.execute("""
        SELECT s.name, s.city, COUNT(a.animal_id) as animal_count
        FROM shelters s LEFT JOIN animals a ON s.shelter_id = a.shelter_id
        GROUP BY s.shelter_id, s.name, s.city ORDER BY animal_count DESC LIMIT 5
    """)
    cols = [d[0] for d in cur.description]
    stats["top_shelters"] = [dict(zip(cols, r)) for r in cur.fetchall()]

    cur.execute("""
        SELECT a.name, sp.name as species, ad.adoption_date
        FROM adoptions ad
        JOIN animals a ON ad.animal_id = a.animal_id
        JOIN species sp ON a.species_id = sp.species_id
        ORDER BY ad.adoption_date DESC LIMIT 5
    """)
    cols = [d[0] for d in cur.description]
    stats["recent_adoptions"] = [dict(zip(cols, r)) for r in cur.fetchall()]

    cur.close()
    conn.close()
    return render_template("dashboard.html", stats=stats)


# ---------------------------------------------------------------------------
# Animals CRUD
# ---------------------------------------------------------------------------

@app.route("/animals")
def animals_list():
    page, per_page, offset = get_pagination()
    status_filter = request.args.get("status", "")
    shelter_filter = request.args.get("shelter_id", "")
    sql = """
        SELECT a.*, s.name AS species_name, b.name AS breed_name,
               c.name AS color_name, sh.name AS shelter_name
        FROM animals a
        JOIN species s ON a.species_id = s.species_id
        LEFT JOIN breeds b ON a.breed_id = b.breed_id
        LEFT JOIN colors c ON a.color_id = c.color_id
        JOIN shelters sh ON a.shelter_id = sh.shelter_id
        WHERE 1=1
    """
    params = []
    if status_filter:
        sql += " AND a.status = %s"
        params.append(status_filter)
    if shelter_filter:
        sql += " AND a.shelter_id = %s"
        params.append(shelter_filter)
    sql += " ORDER BY a.animal_id DESC LIMIT %s OFFSET %s"
    params.extend([per_page, offset])
    rows = query(sql, params)
    return render_template("animals.html", animals=rows, species=get_species(),
                           breeds=get_breeds(), colors=get_colors(),
                           shelters=get_shelters(), status_filter=status_filter,
                           shelter_filter=shelter_filter, page=page, per_page=per_page)


@app.route("/animals/add", methods=["POST"])
def animals_add():
    execute("""
        INSERT INTO animals (name, species_id, breed_id, color_id, date_of_birth,
                             gender, weight_kg, shelter_id, intake_date, status)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        request.form["name"],
        request.form["species_id"],
        request.form.get("breed_id") or None,
        request.form.get("color_id") or None,
        request.form.get("date_of_birth") or None,
        request.form.get("gender") or None,
        request.form.get("weight_kg") or None,
        request.form["shelter_id"],
        request.form["intake_date"],
        request.form.get("status", "available"),
    ))
    flash("Animal added successfully.", "success")
    return redirect(url_for("animals_list"))


@app.route("/animals/<int:id>/edit", methods=["POST"])
def animals_edit(id):
    execute("""
        UPDATE animals SET name=%s, species_id=%s, breed_id=%s, color_id=%s,
               date_of_birth=%s, gender=%s, weight_kg=%s, shelter_id=%s,
               intake_date=%s, status=%s
        WHERE animal_id=%s
    """, (
        request.form["name"],
        request.form["species_id"],
        request.form.get("breed_id") or None,
        request.form.get("color_id") or None,
        request.form.get("date_of_birth") or None,
        request.form.get("gender") or None,
        request.form.get("weight_kg") or None,
        request.form["shelter_id"],
        request.form["intake_date"],
        request.form.get("status", "available"),
        id,
    ))
    flash("Animal updated.", "success")
    return redirect(url_for("animals_list"))


@app.route("/animals/<int:id>/delete", methods=["POST"])
def animals_delete(id):
    execute("DELETE FROM adoptions WHERE animal_id = %s", (id,))
    execute("DELETE FROM medical_records WHERE animal_id = %s", (id,))
    execute("DELETE FROM animals WHERE animal_id = %s", (id,))
    flash("Animal deleted.", "warning")
    return redirect(url_for("animals_list"))


# ---------------------------------------------------------------------------
# Adopters CRUD
# ---------------------------------------------------------------------------

@app.route("/adopters")
def adopters_list():
    page, per_page, offset = get_pagination()
    rows = query("""
        SELECT a.*, COUNT(ad.adoption_id) AS adoption_count
        FROM adopters a LEFT JOIN adoptions ad ON a.adopter_id = ad.adopter_id
        GROUP BY a.adopter_id ORDER BY a.adopter_id DESC
        LIMIT %s OFFSET %s
    """, (per_page, offset))
    return render_template("adopters.html", adopters=rows, page=page, per_page=per_page)


@app.route("/adopters/add", methods=["POST"])
def adopters_add():
    execute("""
        INSERT INTO adopters (first_name, last_name, email, phone, address, city, registered_date)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
    """, (
        request.form["first_name"], request.form["last_name"],
        request.form.get("email") or None, request.form.get("phone") or None,
        request.form.get("address") or None, request.form.get("city") or None,
        request.form["registered_date"],
    ))
    flash("Adopter added.", "success")
    return redirect(url_for("adopters_list"))


@app.route("/adopters/<int:id>/edit", methods=["POST"])
def adopters_edit(id):
    execute("""
        UPDATE adopters SET first_name=%s, last_name=%s, email=%s, phone=%s,
               address=%s, city=%s, registered_date=%s
        WHERE adopter_id=%s
    """, (
        request.form["first_name"], request.form["last_name"],
        request.form.get("email") or None, request.form.get("phone") or None,
        request.form.get("address") or None, request.form.get("city") or None,
        request.form["registered_date"], id,
    ))
    flash("Adopter updated.", "success")
    return redirect(url_for("adopters_list"))


@app.route("/adopters/<int:id>/delete", methods=["POST"])
def adopters_delete(id):
    execute("DELETE FROM adoptions WHERE adopter_id = %s", (id,))
    execute("UPDATE donations SET adopter_id = NULL WHERE adopter_id = %s", (id,))
    execute("DELETE FROM adopters WHERE adopter_id = %s", (id,))
    flash("Adopter deleted.", "warning")
    return redirect(url_for("adopters_list"))


# ---------------------------------------------------------------------------
# Adoptions CRUD
# ---------------------------------------------------------------------------

@app.route("/adoptions")
def adoptions_list():
    page, per_page, offset = get_pagination()
    rows = query("""
        SELECT ad.*, an.name AS animal_name,
               a.first_name || ' ' || a.last_name AS adopter_name
        FROM adoptions ad
        JOIN animals an ON ad.animal_id = an.animal_id
        JOIN adopters a ON ad.adopter_id = a.adopter_id
        ORDER BY ad.adoption_date DESC
        LIMIT %s OFFSET %s
    """, (per_page, offset))
    return render_template("adoptions.html", adoptions=rows,
                           animals=get_animals_list(), adopters=get_adopters_list(),
                           page=page, per_page=per_page)


@app.route("/adoptions/add", methods=["POST"])
def adoptions_add():
    execute("""
        INSERT INTO adoptions (animal_id, adopter_id, adoption_date, fee, notes)
        VALUES (%s,%s,%s,%s,%s)
    """, (
        request.form["animal_id"], request.form["adopter_id"],
        request.form["adoption_date"], request.form["fee"],
        request.form.get("notes") or None,
    ))
    execute("UPDATE animals SET status = 'adopted' WHERE animal_id = %s",
            (request.form["animal_id"],))
    flash("Adoption recorded.", "success")
    return redirect(url_for("adoptions_list"))


@app.route("/adoptions/<int:id>/edit", methods=["POST"])
def adoptions_edit(id):
    execute("""
        UPDATE adoptions SET animal_id=%s, adopter_id=%s, adoption_date=%s, fee=%s, notes=%s
        WHERE adoption_id=%s
    """, (
        request.form["animal_id"], request.form["adopter_id"],
        request.form["adoption_date"], request.form["fee"],
        request.form.get("notes") or None, id,
    ))
    flash("Adoption updated.", "success")
    return redirect(url_for("adoptions_list"))


@app.route("/adoptions/<int:id>/delete", methods=["POST"])
def adoptions_delete(id):
    row = query("SELECT animal_id FROM adoptions WHERE adoption_id = %s", (id,), fetchone=True)
    execute("DELETE FROM adoptions WHERE adoption_id = %s", (id,))
    if row:
        execute("UPDATE animals SET status = 'available' WHERE animal_id = %s",
                (row["animal_id"],))
    flash("Adoption deleted.", "warning")
    return redirect(url_for("adoptions_list"))


# ---------------------------------------------------------------------------
# Medical Records CRUD
# ---------------------------------------------------------------------------

@app.route("/medical")
def medical_list():
    page, per_page, offset = get_pagination()
    rows = query("""
        SELECT mr.*, an.name AS animal_name, mt.name AS type_name,
               COALESCE(s.first_name || ' ' || s.last_name, '—') AS staff_name
        FROM medical_records mr
        JOIN animals an ON mr.animal_id = an.animal_id
        JOIN medical_types mt ON mr.type_id = mt.type_id
        LEFT JOIN staff s ON mr.staff_id = s.staff_id
        ORDER BY mr.record_date DESC
        LIMIT %s OFFSET %s
    """, (per_page, offset))
    return render_template("medical.html", records=rows, animals=get_animals_list(),
                           medical_types=get_medical_types(), staff=get_staff_list(),
                           page=page, per_page=per_page)


@app.route("/medical/add", methods=["POST"])
def medical_add():
    execute("""
        INSERT INTO medical_records (animal_id, type_id, staff_id, record_date, description, cost)
        VALUES (%s,%s,%s,%s,%s,%s)
    """, (
        request.form["animal_id"], request.form["type_id"],
        request.form.get("staff_id") or None, request.form["record_date"],
        request.form.get("description") or None,
        request.form.get("cost") or None,
    ))
    flash("Medical record added.", "success")
    return redirect(url_for("medical_list"))


@app.route("/medical/<int:id>/edit", methods=["POST"])
def medical_edit(id):
    execute("""
        UPDATE medical_records SET animal_id=%s, type_id=%s, staff_id=%s,
               record_date=%s, description=%s, cost=%s
        WHERE record_id=%s
    """, (
        request.form["animal_id"], request.form["type_id"],
        request.form.get("staff_id") or None, request.form["record_date"],
        request.form.get("description") or None,
        request.form.get("cost") or None, id,
    ))
    flash("Medical record updated.", "success")
    return redirect(url_for("medical_list"))


@app.route("/medical/<int:id>/delete", methods=["POST"])
def medical_delete(id):
    execute("DELETE FROM medical_records WHERE record_id = %s", (id,))
    flash("Medical record deleted.", "warning")
    return redirect(url_for("medical_list"))


# ---------------------------------------------------------------------------
# Staff CRUD
# ---------------------------------------------------------------------------

@app.route("/staff")
def staff_list():
    page, per_page, offset = get_pagination()
    rows = query("""
        SELECT s.*, sr.name AS role_name, sh.name AS shelter_name
        FROM staff s
        JOIN staff_roles sr ON s.role_id = sr.role_id
        JOIN shelters sh ON s.shelter_id = sh.shelter_id
        ORDER BY s.staff_id DESC
        LIMIT %s OFFSET %s
    """, (per_page, offset))
    return render_template("staff.html", staff=rows, roles=get_staff_roles(),
                           shelters=get_shelters(), page=page, per_page=per_page)


@app.route("/staff/add", methods=["POST"])
def staff_add():
    execute("""
        INSERT INTO staff (first_name, last_name, role_id, shelter_id, email, phone, hire_date, salary)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        request.form["first_name"], request.form["last_name"],
        request.form["role_id"], request.form["shelter_id"],
        request.form.get("email") or None, request.form.get("phone") or None,
        request.form["hire_date"], request.form.get("salary") or None,
    ))
    flash("Staff member added.", "success")
    return redirect(url_for("staff_list"))


@app.route("/staff/<int:id>/edit", methods=["POST"])
def staff_edit(id):
    execute("""
        UPDATE staff SET first_name=%s, last_name=%s, role_id=%s, shelter_id=%s,
               email=%s, phone=%s, hire_date=%s, salary=%s
        WHERE staff_id=%s
    """, (
        request.form["first_name"], request.form["last_name"],
        request.form["role_id"], request.form["shelter_id"],
        request.form.get("email") or None, request.form.get("phone") or None,
        request.form["hire_date"], request.form.get("salary") or None, id,
    ))
    flash("Staff member updated.", "success")
    return redirect(url_for("staff_list"))


@app.route("/staff/<int:id>/delete", methods=["POST"])
def staff_delete(id):
    execute("UPDATE medical_records SET staff_id = NULL WHERE staff_id = %s", (id,))
    execute("DELETE FROM staff WHERE staff_id = %s", (id,))
    flash("Staff member deleted.", "warning")
    return redirect(url_for("staff_list"))


# ---------------------------------------------------------------------------
# Donations CRUD
# ---------------------------------------------------------------------------

@app.route("/donations")
def donations_list():
    page, per_page, offset = get_pagination()
    rows = query("""
        SELECT d.*, sh.name AS shelter_name,
               COALESCE(a.first_name || ' ' || a.last_name, 'Anonymous') AS donor_name
        FROM donations d
        JOIN shelters sh ON d.shelter_id = sh.shelter_id
        LEFT JOIN adopters a ON d.adopter_id = a.adopter_id
        ORDER BY d.donation_date DESC
        LIMIT %s OFFSET %s
    """, (per_page, offset))
    return render_template("donations.html", donations=rows,
                           shelters=get_shelters(), adopters=get_adopters_list(),
                           page=page, per_page=per_page)


@app.route("/donations/add", methods=["POST"])
def donations_add():
    execute("""
        INSERT INTO donations (adopter_id, shelter_id, amount, donation_date, purpose)
        VALUES (%s,%s,%s,%s,%s)
    """, (
        request.form.get("adopter_id") or None, request.form["shelter_id"],
        request.form["amount"], request.form["donation_date"],
        request.form.get("purpose") or None,
    ))
    flash("Donation recorded.", "success")
    return redirect(url_for("donations_list"))


@app.route("/donations/<int:id>/edit", methods=["POST"])
def donations_edit(id):
    execute("""
        UPDATE donations SET adopter_id=%s, shelter_id=%s, amount=%s,
               donation_date=%s, purpose=%s
        WHERE donation_id=%s
    """, (
        request.form.get("adopter_id") or None, request.form["shelter_id"],
        request.form["amount"], request.form["donation_date"],
        request.form.get("purpose") or None, id,
    ))
    flash("Donation updated.", "success")
    return redirect(url_for("donations_list"))


@app.route("/donations/<int:id>/delete", methods=["POST"])
def donations_delete(id):
    execute("DELETE FROM donations WHERE donation_id = %s", (id,))
    flash("Donation deleted.", "warning")
    return redirect(url_for("donations_list"))


# ---------------------------------------------------------------------------
# Tools — Generator, Benchmark, Export/Import
# ---------------------------------------------------------------------------

@app.route("/tools")
def tools_page():
    return render_template("tools.html")


@app.route("/tools/generate", methods=["POST"])
def tools_generate():
    count = request.form.get("count", "1000")
    try:
        result = subprocess.run(
            [sys.executable, "generator.py", "--count", count],
            capture_output=True, text=True, timeout=300,
        )
        output = result.stdout + result.stderr
        flash(f"Generator output:\n{output}", "info")
    except subprocess.TimeoutExpired:
        flash("Generator timed out (5 min limit).", "danger")
    except Exception as e:
        flash(f"Generator error: {e}", "danger")
    return redirect(url_for("tools_page"))


@app.route("/tools/benchmark", methods=["POST"])
def tools_benchmark():
    try:
        result = subprocess.run(
            [sys.executable, "benchmark.py"],
            capture_output=True, text=True, timeout=600,
        )
        output = result.stdout + result.stderr
        flash(f"Benchmark output:\n{output}", "info")
    except subprocess.TimeoutExpired:
        flash("Benchmark timed out (10 min limit).", "danger")
    except Exception as e:
        flash(f"Benchmark error: {e}", "danger")
    return redirect(url_for("tools_page"))


@app.route("/tools/drop-all", methods=["POST"])
def tools_drop_all():
    conn = get_connection()
    conn.autocommit = False
    cur = conn.cursor()
    try:
        sql_dir = os.path.join(os.path.dirname(__file__), "sql")
        schema_path = os.path.join(sql_dir, "create_schema.sql")
        seed_path = os.path.join(sql_dir, "seed_dictionaries.sql")

        with open(schema_path, "r", encoding="utf-8") as f:
            cur.execute(f.read())
        with open(seed_path, "r", encoding="utf-8") as f:
            cur.execute(f.read())

        conn.commit()
        flash("All data dropped and database reset successfully.", "warning")
    except Exception as e:
        conn.rollback()
        flash(f"Drop all error: {e}", "danger")
    finally:
        cur.close()
        conn.close()

    return redirect(url_for("tools_page"))


@app.route("/tools/export", methods=["POST"])
def tools_export():
    fmt = request.form.get("format", "json")
    conn = get_db()
    cur = conn.cursor()
    tables = [
        "species", "breeds", "colors", "medical_types", "staff_roles",
        "shelters", "animals", "adopters", "adoptions", "staff",
        "medical_records", "donations",
    ]
    data = {}
    for t in tables:
        cur.execute(f"SELECT * FROM {t}")
        cols = [d[0] for d in cur.description]
        rows = cur.fetchall()
        data[t] = [dict(zip(cols, r)) for r in rows]
    cur.close()
    conn.close()

    os.makedirs("exports", exist_ok=True)

    if fmt == "json":
        path = os.path.join("exports", "pawhome_export.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
        flash("Exported to JSON.", "success")
        return send_file(path, as_attachment=True, download_name="pawhome_export.json")
    else:
        import xml.etree.ElementTree as ET
        root = ET.Element("pawhome")
        for table_name, rows in data.items():
            table_el = ET.SubElement(root, table_name)
            for row in rows:
                row_el = ET.SubElement(table_el, "row")
                for col, val in row.items():
                    col_el = ET.SubElement(row_el, col)
                    col_el.text = str(val) if val is not None else ""
        tree = ET.ElementTree(root)
        path = os.path.join("exports", "pawhome_export.xml")
        tree.write(path, encoding="unicode", xml_declaration=True)
        flash("Exported to XML.", "success")
        return send_file(path, as_attachment=True, download_name="pawhome_export.xml")


@app.route("/tools/import", methods=["POST"])
def tools_import():
    file = request.files.get("file")
    if not file:
        flash("No file selected.", "danger")
        return redirect(url_for("tools_page"))

    content = file.read().decode("utf-8")
    fmt = "json" if file.filename.endswith(".json") else "xml"

    conn = get_db()
    cur = conn.cursor()
    conn.autocommit = False

    try:
        if fmt == "json":
            data = json.loads(content)
        else:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(content)
            data = {}
            for table_el in root:
                table_name = table_el.tag
                rows = []
                for row_el in table_el:
                    row = {}
                    for col_el in row_el:
                        val = col_el.text
                        if val == "" or val == "None":
                            val = None
                        row[col_el.tag] = val
                    rows.append(row)
                data[table_name] = rows

        insert_order = [
            "species", "breeds", "colors", "medical_types", "staff_roles",
            "shelters", "animals", "adopters", "adoptions", "staff",
            "medical_records", "donations",
        ]
        for table_name in insert_order:
            if table_name not in data:
                continue
            rows = data[table_name]
            if not rows:
                continue
            cols = list(rows[0].keys())
            placeholders = ", ".join(["%s"] * len(cols))
            col_names = ", ".join(cols)
            for row in rows:
                vals = [row.get(c) for c in cols]
                cur.execute(
                    f"INSERT INTO {table_name} ({col_names}) VALUES ({placeholders}) ON CONFLICT DO NOTHING",
                    vals,
                )
        conn.commit()
        flash(f"Imported {fmt.upper()} successfully.", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Import error: {e}", "danger")
    finally:
        cur.close()
        conn.close()

    return redirect(url_for("tools_page"))


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(
        debug=os.environ.get("FLASK_DEBUG", "1").lower() in ("1", "true", "yes"),
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "5000")),
    )
