from typing import List, Dict, Any, Optional
from db.connection import get_connection

ClassRow = Dict[str, Any]


def create_class(data: ClassRow) -> int:
    sql = (
        "INSERT INTO classes(name, level, section, room, academic_year) VALUES(?,?,?,?,?)"
    )
    params = (
        data.get("name"),
        data.get("level"),
        data.get("section"),
        data.get("room"),
        data.get("academic_year"),
    )
    conn = get_connection()
    try:
        cur = conn.execute(sql, params)
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def update_class(class_id: int, data: ClassRow) -> None:
    sql = (
        "UPDATE classes SET name=?, level=?, section=?, room=?, academic_year=?, updated_at=datetime('now') WHERE id=?"
    )
    params = (
        data.get("name"),
        data.get("level"),
        data.get("section"),
        data.get("room"),
        data.get("academic_year"),
        class_id,
    )
    conn = get_connection()
    try:
        conn.execute(sql, params)
        conn.commit()
    finally:
        conn.close()


def delete_class(class_id: int) -> None:
    conn = get_connection()
    try:
        conn.execute("DELETE FROM classes WHERE id=?", (class_id,))
        conn.commit()
    finally:
        conn.close()


def get_class(class_id: int) -> Optional[ClassRow]:
    conn = get_connection()
    try:
        cur = conn.execute(
            "SELECT id, name, level, section, room, academic_year, created_at, updated_at FROM classes WHERE id=?",
            (class_id,),
        )
        row = cur.fetchone()
        if not row:
            return None
        keys = ["id", "name", "level", "section", "room", "academic_year", "created_at", "updated_at"]
        return dict(zip(keys, row))
    finally:
        conn.close()


def list_classes(query: str = "", year: Optional[str] = None, limit: int = 100, offset: int = 0) -> List[ClassRow]:
    like = f"%{query}%"
    conn = get_connection()
    try:
        if year:
            cur = conn.execute(
                "SELECT id, name, level, section, room, academic_year FROM classes "
                "WHERE (name LIKE ? OR level LIKE ? OR section LIKE ?) AND academic_year=? "
                "ORDER BY name LIMIT ? OFFSET ?",
                (like, like, like, year, limit, offset),
            )
        else:
            cur = conn.execute(
                "SELECT id, name, level, section, room, academic_year FROM classes "
                "WHERE (name LIKE ? OR level LIKE ? OR section LIKE ?) "
                "ORDER BY name LIMIT ? OFFSET ?",
                (like, like, like, limit, offset),
            )
        keys = ["id", "name", "level", "section", "room", "academic_year"]
        results = [dict(zip(keys, row)) for row in cur.fetchall()]
        return results
    finally:
        conn.close()


def enroll_student(class_id: int, student_id: int) -> None:
    conn = get_connection()
    try:
        # Check if enrollment already exists
        cur = conn.execute(
            "SELECT 1 FROM class_enrollments WHERE class_id=? AND student_id=?",
            (class_id, student_id),
        )
        if cur.fetchone():
            return
        
        # Insert new enrollment
        conn.execute(
            "INSERT INTO class_enrollments(class_id, student_id) VALUES(?,?)",
            (class_id, student_id),
        )
        conn.commit()
    except Exception:
        # Re-raise to let callers handle message display
        raise
    finally:
        conn.close()


def unenroll_student(class_id: int, student_id: int) -> None:
    conn = get_connection()
    try:
        conn.execute("DELETE FROM class_enrollments WHERE class_id=? AND student_id=?", (class_id, student_id))
        conn.commit()
    finally:
        conn.close()


def list_enrolled_students(class_id: int) -> List[Dict[str, Any]]:
    conn = get_connection()
    try:
        cur = conn.execute(
            "SELECT s.id, s.enrollment_no, s.last_name, s.first_name FROM class_enrollments ce "
            "JOIN students s ON s.id = ce.student_id WHERE ce.class_id=? ORDER BY s.last_name, s.first_name",
            (class_id,),
        )
        keys = ["id", "enrollment_no", "last_name", "first_name"]
        return [dict(zip(keys, row)) for row in cur.fetchall()]
    finally:
        conn.close()


def get_enrollment_count(class_id: int) -> int:
    """Get the number of enrolled students in a class"""
    conn = get_connection()
    try:
        cur = conn.execute(
            "SELECT COUNT(*) FROM class_enrollments WHERE class_id=?",
            (class_id,),
        )
        return cur.fetchone()[0]
    finally:
        conn.close()


def list_classes_with_enrollment_count(query: str = "", year: Optional[str] = None, limit: int = 100, offset: int = 0) -> List[ClassRow]:
    """List classes with enrollment count and attendance statistics"""
    like = f"%{query}%"
    conn = get_connection()
    try:
        if year:
            cur = conn.execute(
                "SELECT c.id, c.name, c.level, c.section, c.room, c.academic_year, "
                "COUNT(DISTINCT ce.student_id) as enrollment_count, "
                "COUNT(DISTINCT as2.id) as session_count "
                "FROM classes c "
                "LEFT JOIN class_enrollments ce ON c.id = ce.class_id "
                "LEFT JOIN attendance_sessions as2 ON c.id = as2.class_id "
                "WHERE (c.name LIKE ? OR c.level LIKE ? OR c.section LIKE ?) AND c.academic_year=? "
                "GROUP BY c.id, c.name, c.level, c.section, c.room, c.academic_year "
                "ORDER BY c.name LIMIT ? OFFSET ?",
                (like, like, like, year, limit, offset),
            )
        else:
            cur = conn.execute(
                "SELECT c.id, c.name, c.level, c.section, c.room, c.academic_year, "
                "COUNT(DISTINCT ce.student_id) as enrollment_count, "
                "COUNT(DISTINCT as2.id) as session_count "
                "FROM classes c "
                "LEFT JOIN class_enrollments ce ON c.id = ce.class_id "
                "LEFT JOIN attendance_sessions as2 ON c.id = as2.class_id "
                "WHERE (c.name LIKE ? OR c.level LIKE ? OR c.section LIKE ?) "
                "GROUP BY c.id, c.name, c.level, c.section, c.room, c.academic_year "
                "ORDER BY c.name LIMIT ? OFFSET ?",
                (like, like, like, limit, offset),
            )
        keys = ["id", "name", "level", "section", "room", "academic_year", "enrollment_count", "session_count"]
        results = [dict(zip(keys, row)) for row in cur.fetchall()]
        return results
    finally:
        conn.close()