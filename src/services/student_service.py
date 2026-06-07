from typing import List, Optional, Dict, Any
from datetime import datetime
from db.connection import get_connection

Student = Dict[str, Any]


def _generate_enrollment_no(conn) -> str:
    """Generate a simple unique enrollment number if not provided.
    Pattern: SYYYYNNNN (e.g., S20250001)
    """
    year = datetime.now().year
    prefix = f"S{year}"
    # Start from count+1 and increment until unique
    (count_current,) = conn.execute(
        "SELECT COUNT(*) FROM students WHERE enrollment_no LIKE ?",
        (f"{prefix}%",),
    ).fetchone()
    n = int(count_current) + 1
    while True:
        candidate = f"{prefix}{n:04d}"
        exists = conn.execute(
            "SELECT 1 FROM students WHERE enrollment_no=?",
            (candidate,),
        ).fetchone()
        if not exists:
            return candidate
        n += 1


def create_student(data: Student) -> int:
    # Auto-generate enrollment_no if missing
    conn = get_connection()
    try:
        enrollment_no = data.get("enrollment_no")
        if not enrollment_no:
            enrollment_no = _generate_enrollment_no(conn)
        sql = (
            "INSERT INTO students(enrollment_no, first_name, last_name, date_of_birth, gender, address, phone, email, student_phone) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
        )
        params = (
            enrollment_no,
            data.get("first_name"),
            data.get("last_name"),
            data.get("date_of_birth"),
            data.get("gender"),
            data.get("address"),
            data.get("phone"),  # parent phone
            data.get("email"),
            data.get("student_phone"),
        )
        cur = conn.execute(sql, params)
        conn.commit()
        student_id = cur.lastrowid
        # Optional logging if user context provided in data
        try:
            from services.log_service import log_action
            actor_id = data.get("_actor_user_id")
            if actor_id:
                log_action("student_create", user_id=actor_id, entity="student", entity_id=student_id,
                           details=f"enrollment_no={enrollment_no}")
        except Exception:
            pass
        return student_id
    finally:
        conn.close()


def update_student(student_id: int, data: Student) -> None:
    """Update student. If enrollment_no not provided, keep existing value."""
    fields = [
        ("first_name", data.get("first_name")),
        ("last_name", data.get("last_name")),
        ("date_of_birth", data.get("date_of_birth")),
        ("gender", data.get("gender")),
        ("address", data.get("address")),
        ("phone", data.get("phone")),  # parent phone
        ("email", data.get("email")),
        ("student_phone", data.get("student_phone")),
    ]
    set_clauses = [f"{k}=?" for k, _ in fields]
    params: list = [v for _, v in fields]

    # include enrollment_no only if present and non-empty
    if data.get("enrollment_no"):
        set_clauses.insert(0, "enrollment_no=?")
        params.insert(0, data.get("enrollment_no"))

    set_sql = ", ".join(set_clauses) + ", updated_at=datetime('now')"
    sql = f"UPDATE students SET {set_sql} WHERE id=?"
    params.append(student_id)

    conn = get_connection()
    try:
        conn.execute(sql, tuple(params))
        conn.commit()
        # Optional logging
        try:
            from services.log_service import log_action
            actor_id = data.get("_actor_user_id")
            if actor_id:
                log_action("student_update", user_id=actor_id, entity="student", entity_id=student_id,
                           details=",".join([k for k, v in fields if v is not None]))
        except Exception:
            pass
    finally:
        conn.close()


def delete_student(student_id: int, actor_user_id: Optional[int] = None) -> None:
    conn = get_connection()
    try:
        conn.execute("DELETE FROM students WHERE id=?", (student_id,))
        conn.commit()
        # Optional logging
        try:
            if actor_user_id:
                from services.log_service import log_action
                log_action("student_delete", user_id=actor_user_id, entity="student", entity_id=student_id)
        except Exception:
            pass
    finally:
        conn.close()


def get_student(student_id: int) -> Optional[Student]:
    conn = get_connection()
    try:
        cur = conn.execute(
            "SELECT id, enrollment_no, first_name, last_name, date_of_birth, gender, address, phone, email, student_phone, created_at, updated_at FROM students WHERE id=?",
            (student_id,),
        )
        row = cur.fetchone()
        if not row:
            return None
        keys = [
            "id",
            "enrollment_no",
            "first_name",
            "last_name",
            "date_of_birth",
            "gender",
            "address",
            "phone",
            "email",
            "student_phone",
            "created_at",
            "updated_at",
        ]
        return dict(zip(keys, row))
    finally:
        conn.close()


def list_students(
    query: str = "",
    limit: int = 50,
    offset: int = 0,
    gender: Optional[str] = None,
    class_id: Optional[int] = None,
) -> List[Student]:
    like = f"%{query}%"
    sql = [
        "SELECT s.id, s.enrollment_no, s.first_name, s.last_name, s.date_of_birth, s.gender, s.phone, s.email, s.student_phone",
        "FROM students s",
        "WHERE (s.last_name LIKE ? OR s.first_name LIKE ? OR s.enrollment_no LIKE ?)",
    ]
    params: list = [like, like, like]

    # class filter using EXISTS to avoid duplicates
    if class_id is not None:
        sql.append(
            "AND EXISTS (SELECT 1 FROM class_enrollments ce WHERE ce.student_id = s.id AND ce.class_id = ?)"
        )
        params.append(class_id)

    # gender filter
    if gender:
        sql.append("AND s.gender = ?")
        params.append(gender)

    sql.append("ORDER BY s.last_name, s.first_name LIMIT ? OFFSET ?")
    params.extend([limit, offset])

    conn = get_connection()
    try:
        cur = conn.execute("\n".join(sql), tuple(params))
        keys = [
            "id",
            "enrollment_no",
            "first_name",
            "last_name",
            "date_of_birth",
            "gender",
            "phone",
            "email",
            "student_phone",
        ]
        return [dict(zip(keys, row)) for row in cur.fetchall()]
    finally:
        conn.close()