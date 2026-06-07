import os
import sqlite3
from pathlib import Path

from utils.config import DB_PATH


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash BLOB NOT NULL,
    salt BLOB NOT NULL,
    role_id INTEGER NOT NULL,
    FOREIGN KEY (role_id) REFERENCES roles(id)
);

-- Subadmin permissions (action-level)
CREATE TABLE IF NOT EXISTS permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    can_manage_students INTEGER NOT NULL DEFAULT 0,
    can_manage_classes INTEGER NOT NULL DEFAULT 0,
    can_manage_attendance INTEGER NOT NULL DEFAULT 0,
    can_manage_fees INTEGER NOT NULL DEFAULT 0,
    can_manage_users INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id)
);

-- Élèves
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    enrollment_no TEXT UNIQUE NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    date_of_birth TEXT,               -- format YYYY-MM-DD
    gender TEXT,                      -- M/F/Autre
    address TEXT,
    phone TEXT,
    email TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_students_name ON students(last_name, first_name);

-- Classes
CREATE TABLE IF NOT EXISTS classes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    level TEXT,                 -- e.g. 1ère, 2ème, etc.
    section TEXT,               -- A, B, C ...
    room TEXT,
    academic_year TEXT,         -- e.g. 2024-2025
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_classes_unique ON classes(name, academic_year);

-- Inscriptions (élèves dans les classes)
CREATE TABLE IF NOT EXISTS class_enrollments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    class_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    enrolled_on TEXT DEFAULT (date('now')),
    status TEXT DEFAULT 'active',
    UNIQUE(class_id, student_id),
    FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_enrollments_class ON class_enrollments(class_id);
CREATE INDEX IF NOT EXISTS idx_enrollments_student ON class_enrollments(student_id);

-- Séances de présence (par classe et date)
CREATE TABLE IF NOT EXISTS attendance_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    class_id INTEGER NOT NULL,
    session_date TEXT NOT NULL, -- YYYY-MM-DD
    created_at TEXT DEFAULT (datetime('now')),
    UNIQUE(class_id, session_date),
    FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE
);

-- Présences par élève pour une séance
CREATE TABLE IF NOT EXISTS attendance_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'Present', -- Present, Absent, Late, Excused
    note TEXT,
    UNIQUE(session_id, student_id),
    FOREIGN KEY (session_id) REFERENCES attendance_sessions(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_attendance_session ON attendance_records(session_id);

-- Frais et paiements
CREATE TABLE IF NOT EXISTS fee_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    class_id INTEGER NOT NULL,
    amount_cents INTEGER NOT NULL,      -- montant par séance en centimes
    currency TEXT NOT NULL DEFAULT 'MAD',
    active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now')),
    UNIQUE(class_id),
    FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE
);

-- Factures générées à partir des présences
CREATE TABLE IF NOT EXISTS fee_invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    amount_cents INTEGER NOT NULL,
    currency TEXT NOT NULL DEFAULT 'MAD',
    status TEXT NOT NULL DEFAULT 'unpaid', -- unpaid, paid, void
    created_at TEXT DEFAULT (datetime('now')),
    paid_at TEXT,
    UNIQUE(session_id, student_id),
    FOREIGN KEY (session_id) REFERENCES attendance_sessions(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_fee_invoices_student ON fee_invoices(student_id);

-- Admin Notes
CREATE TABLE IF NOT EXISTS admin_notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    content TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'todo', -- todo, doing, done
    priority TEXT NOT NULL DEFAULT 'normal', -- low, normal, high
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_admin_notes_status ON admin_notes(status);
"""


def get_connection():
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db():
    conn = get_connection()
    try:
        conn.executescript(SCHEMA_SQL)
        # Migrations
        # 1) students.student_phone (separate phone for student)
        cur = conn.execute("PRAGMA table_info(students)")
        cols = [row[1] for row in cur.fetchall()]
        if "student_phone" not in cols:
            conn.execute("ALTER TABLE students ADD COLUMN student_phone TEXT")
        # 2) permissions table (if missing)
        conn.execute(
            "CREATE TABLE IF NOT EXISTS permissions (\n"
            "    id INTEGER PRIMARY KEY AUTOINCREMENT,\n"
            "    user_id INTEGER NOT NULL,\n"
            "    can_manage_students INTEGER NOT NULL DEFAULT 0,\n"
            "    can_manage_classes INTEGER NOT NULL DEFAULT 0,\n"
            "    can_manage_attendance INTEGER NOT NULL DEFAULT 0,\n"
            "    can_manage_fees INTEGER NOT NULL DEFAULT 0,\n"
            "    can_manage_users INTEGER NOT NULL DEFAULT 0,\n"
            "    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,\n"
            "    UNIQUE(user_id)\n"
            ")"
        )
        
        # 3) attendance_records: add user_id and updated_at if missing
        cur = conn.execute("PRAGMA table_info(attendance_records)")
        cols = [row[1] for row in cur.fetchall()]
        if "user_id" not in cols:
            conn.execute("ALTER TABLE attendance_records ADD COLUMN user_id INTEGER")
        if "updated_at" not in cols:
            conn.execute("ALTER TABLE attendance_records ADD COLUMN updated_at TEXT")
            conn.execute("UPDATE attendance_records SET updated_at = datetime('now') WHERE updated_at IS NULL")
            # Trigger to auto-update updated_at on row changes
            conn.execute(
                "CREATE TRIGGER IF NOT EXISTS trg_attendance_records_updated_at "
                "AFTER UPDATE ON attendance_records "
                "BEGIN "
                "  UPDATE attendance_records SET updated_at = datetime('now') WHERE id = NEW.id; "
                "END"
            )
            # Ensure updated_at is set on insert as well
            conn.execute(
                "CREATE TRIGGER IF NOT EXISTS trg_attendance_records_insert_set_updated_at "
                "AFTER INSERT ON attendance_records "
                "BEGIN "
                "  UPDATE attendance_records SET updated_at = datetime('now') WHERE id = NEW.id; "
                "END"
            )
        
        # 4) Add created_at to users if missing (used by dashboard)
        cur = conn.execute("PRAGMA table_info(users)")
        cols = [row[1] for row in cur.fetchall()]
        if "created_at" not in cols:
            conn.execute("ALTER TABLE users ADD COLUMN created_at TEXT")
            conn.execute("UPDATE users SET created_at = datetime('now') WHERE created_at IS NULL")
            conn.execute(
                "CREATE TRIGGER IF NOT EXISTS trg_users_created_at "
                "AFTER INSERT ON users "
                "WHEN NEW.created_at IS NULL "
                "BEGIN "
                "  UPDATE users SET created_at = datetime('now') WHERE id = NEW.id; "
                "END"
            )
        
        # 5) Add created_at to class_enrollments if missing (used by dashboard)
        cur = conn.execute("PRAGMA table_info(class_enrollments)")
        cols = [row[1] for row in cur.fetchall()]
        if "created_at" not in cols:
            conn.execute("ALTER TABLE class_enrollments ADD COLUMN created_at TEXT")
            conn.execute("UPDATE class_enrollments SET created_at = datetime('now') WHERE created_at IS NULL")
            conn.execute(
                "CREATE TRIGGER IF NOT EXISTS trg_class_enrollments_created_at "
                "AFTER INSERT ON class_enrollments "
                "WHEN NEW.created_at IS NULL "
                "BEGIN "
                "  UPDATE class_enrollments SET created_at = datetime('now') WHERE id = NEW.id; "
                "END"
            )

        # 6) Create audit logs table if missing
        conn.execute(
            "CREATE TABLE IF NOT EXISTS logs (\n"
            "  id INTEGER PRIMARY KEY AUTOINCREMENT,\n"
            "  timestamp TEXT DEFAULT (datetime('now')),\n"
            "  user_id INTEGER,\n"
            "  action TEXT NOT NULL,\n"
            "  entity TEXT,\n"
            "  entity_id INTEGER,\n"
            "  details TEXT,\n"
            "  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL\n"
            ")"
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON logs(timestamp)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_logs_entity ON logs(entity, entity_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_logs_user ON logs(user_id)")

        # 7) Ensure admin_notes table exists (migration-safe)
        conn.execute(
            "CREATE TABLE IF NOT EXISTS admin_notes (\n"
            "  id INTEGER PRIMARY KEY AUTOINCREMENT,\n"
            "  title TEXT,\n"
            "  content TEXT NOT NULL,\n"
            "  status TEXT NOT NULL DEFAULT 'todo',\n"
            "  priority TEXT NOT NULL DEFAULT 'normal',\n"
            "  created_at TEXT DEFAULT (datetime('now')),\n"
            "  updated_at TEXT DEFAULT (datetime('now'))\n"
            ")"
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_admin_notes_status ON admin_notes(status)")
        
        conn.commit()
    finally:
        conn.close()