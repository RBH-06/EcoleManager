from db.connection import get_connection

FRENCH_ROLES = [
    (1, "Admin"),
    (2, "Subadmin"),
]


def seed_initial_admin():
    """Ensure roles exist and an initial admin user is present.

    Default admin: username "admin", password "admin" (change it after first login)
    """
    from services.auth_service import ensure_admin_user

    conn = get_connection()
    try:
        # Seed roles in French
        for _, role_name in FRENCH_ROLES:
            conn.execute("INSERT OR IGNORE INTO roles(name) VALUES (?)", (role_name,))
        conn.commit()
    finally:
        conn.close()

    # Ensure admin user exists
    ensure_admin_user(username="admin", password="admin")


def seed_demo_data():
    """Insert demo students and classes if they don't already exist, and enroll some students.

    Safe to run multiple times thanks to unique constraints and INSERT OR IGNORE.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()

        # Demo classes
        classes = [
            {"name": "1A", "level": "1ère", "section": "A", "room": "101", "academic_year": "2024-2025"},
            {"name": "1B", "level": "1ère", "section": "B", "room": "102", "academic_year": "2024-2025"},
            {"name": "2A", "level": "2ème", "section": "A", "room": "201", "academic_year": "2024-2025"},
            {"name": "3A", "level": "3ème", "section": "A", "room": "301", "academic_year": "2024-2025"},
        ]
        for c in classes:
            cur.execute(
                "INSERT OR IGNORE INTO classes(name, level, section, room, academic_year) VALUES(?,?,?,?,?)",
                (c["name"], c.get("level"), c.get("section"), c.get("room"), c.get("academic_year")),
            )

        # Demo students
        students = [
            ("S2024001", "Amine", "Bennani", "2008-04-03", "M", "Rabat", "+212600000001", "amine1@example.com"),
            ("S2024002", "Sara", "El Fassi", "2008-06-12", "F", "Casablanca", "+212600000002", "sara@example.com"),
            ("S2024003", "Youssef", "Haddad", "2007-11-21", "M", "Fès", "+212600000003", "youssef@example.com"),
            ("S2024004", "Aya", "Zaid", "2009-02-10", "F", "Marrakech", "+212600000004", "aya@example.com"),
            ("S2024005", "Omar", "Boukhriss", "2008-09-30", "M", "Rabat", "+212600000005", "omar@example.com"),
            ("S2024006", "Hiba", "Karim", "2007-12-15", "F", "Salé", "+212600000006", "hiba@example.com"),
            ("S2024007", "Adam", "Jabri", "2008-03-22", "M", "Agadir", "+212600000007", "adam@example.com"),
            ("S2024008", "Nada", "Aziz", "2009-07-09", "F", "Tanger", "+212600000008", "nada@example.com"),
        ]
        for s in students:
            cur.execute(
                "INSERT OR IGNORE INTO students(enrollment_no, first_name, last_name, date_of_birth, gender, address, phone, email) "
                "VALUES (?,?,?,?,?,?,?,?)",
                s,
            )

        conn.commit()

        # Map names to IDs
        def get_class_id(name, year):
            r = cur.execute(
                "SELECT id FROM classes WHERE name=? AND academic_year=?",
                (name, year),
            ).fetchone()
            return r[0] if r else None

        def get_student_id(enrollment_no):
            r = cur.execute("SELECT id FROM students WHERE enrollment_no=?", (enrollment_no,)).fetchone()
            return r[0] if r else None

        # Enrollments sample
        enrollments = {
            ("1A", "2024-2025"): ["S2024001", "S2024002", "S2024003"],
            ("1B", "2024-2025"): ["S2024004", "S2024005"],
            ("2A", "2024-2025"): ["S2024006"],
            ("3A", "2024-2025"): ["S2024007", "S2024008"],
        }
        for (cname, year), ens in enrollments.items():
            cid = get_class_id(cname, year)
            if not cid:
                continue
            for enr in ens:
                sid = get_student_id(enr)
                if not sid:
                    continue
                cur.execute(
                    "INSERT OR IGNORE INTO class_enrollments(class_id, student_id) VALUES(?,?)",
                    (cid, sid),
                )

        conn.commit()
    finally:
        conn.close()


def seed_students():
    """Seed 100 students into the database."""
    conn = get_connection()
    try:
        for i in range(1, 101):
            conn.execute(
                "INSERT INTO students (enrollment_no, first_name, last_name, date_of_birth, gender, phone) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    f"ENR{i:03d}",
                    f"FirstName{i}",
                    f"LastName{i}",
                    "2005-01-01",  # Example DOB
                    "M" if i % 2 == 0 else "F",  # Alternate genders
                    f"+123456789{i:03d}",
                ),
            )
        conn.commit()
    finally:
        conn.close()


def seed_users():
    """Seed the database with a default admin user."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (username, password, role)
        VALUES ('admin', 'admin123', 'admin')
    """)
    conn.commit()
    conn.close()


if __name__ == "__main__":
    seed_users()
    print("Database seeded successfully!")