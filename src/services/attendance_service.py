from typing import List, Dict, Any, Optional
from db.connection import get_connection

Record = Dict[str, Any]


def get_or_create_session(class_id: int, session_date: str, user_id: Optional[int] = None) -> int:
    conn = get_connection()
    try:
        cur = conn.execute(
            "SELECT id FROM attendance_sessions WHERE class_id=? AND session_date=?",
            (class_id, session_date),
        )
        row = cur.fetchone()
        if row:
            return row[0]
            
        # Create new session
        cur = conn.execute(
            "INSERT INTO attendance_sessions(class_id, session_date) VALUES(?,?)",
            (class_id, session_date),
        )
        session_id = cur.lastrowid
        conn.commit()
        
        # Log session creation
        try:
            class_info = conn.execute(
                "SELECT name FROM classes WHERE id=?", (class_id,)
            ).fetchone()
            
            if class_info:
                class_name = class_info[0]
                details = f"Classe: {class_name}, Date: {session_date}"
                
                from services.log_service import log_action
                log_action("session_created", user_id=user_id, entity="session", entity_id=session_id, details=details)
        except Exception:
            # Don't fail if logging fails
            pass
            
        return session_id
    finally:
        conn.close()


def list_sessions(class_id: int, limit: int = 30, offset: int = 0) -> List[Dict[str, Any]]:
    conn = get_connection()
    try:
        cur = conn.execute(
            "SELECT id, session_date, created_at FROM attendance_sessions WHERE class_id=? ORDER BY session_date DESC LIMIT ? OFFSET ?",
            (class_id, limit, offset),
        )
        keys = ["id", "session_date", "created_at"]
        return [dict(zip(keys, row)) for row in cur.fetchall()]
    finally:
        conn.close()


def ensure_records_for_enrolled(session_id: int, class_id: int, default_status: str = "Present") -> None:
    """Insert attendance rows for enrolled students missing records for this session.
    Does not overwrite existing records.
    """
    conn = get_connection()
    try:
        conn.execute(
            """
            INSERT INTO attendance_records(session_id, student_id, status)
            SELECT ?, ce.student_id, ?
            FROM class_enrollments ce
            WHERE ce.class_id=?
              AND NOT EXISTS (
                    SELECT 1 FROM attendance_records ar
                    WHERE ar.session_id=? AND ar.student_id=ce.student_id
              )
            """,
            (session_id, default_status, class_id, session_id),
        )
        conn.commit()
    finally:
        conn.close()


def upsert_attendance(session_id: int, student_id: int, status: str, note: Optional[str] = None, user_id: Optional[int] = None) -> None:
    conn = get_connection()
    try:
        # Get student info for logging
        student_info = conn.execute(
            "SELECT enrollment_no, first_name, last_name FROM students WHERE id=?",
            (student_id,)
        ).fetchone()
        
        # Get session info for logging
        session_info = conn.execute(
            "SELECT s.session_date, c.name as class_name FROM attendance_sessions s "
            "JOIN classes c ON c.id = s.class_id WHERE s.id=?",
            (session_id,)
        ).fetchone()
        
        # Check if this is an update or insert
        existing = conn.execute(
            "SELECT status FROM attendance_records WHERE session_id=? AND student_id=?",
            (session_id, student_id)
        ).fetchone()
        
        conn.execute(
            "INSERT INTO attendance_records(session_id, student_id, status, note) VALUES(?,?,?,?) "
            "ON CONFLICT(session_id, student_id) DO UPDATE SET status=excluded.status, note=excluded.note",
            (session_id, student_id, status, note),
        )
        conn.commit()
        
        # Log the attendance action
        if student_info and session_info:
            enrollment_no, first_name, last_name = student_info
            session_date, class_name = session_info
            student_name = f"{first_name} {last_name} ({enrollment_no})"
            
            action_type = "attendance_updated" if existing else "attendance_created"
            old_status = existing[0] if existing else "Non enregistré"
            details = f"Élève: {student_name}, Classe: {class_name}, Date: {session_date}, Statut: {old_status} → {status}"
            if note:
                details += f", Note: {note}"
                
            try:
                from services.log_service import log_action
                log_action(action_type, user_id=user_id, entity="attendance", entity_id=session_id, details=details)
            except Exception:
                # Don't fail if logging fails
                pass
                
    finally:
        conn.close()


def list_attendance(session_id: int) -> List[Record]:
    conn = get_connection()
    try:
        cur = conn.execute(
            "SELECT ar.student_id, s.enrollment_no, s.last_name, s.first_name, ar.status, ar.note "
            "FROM attendance_records ar "
            "JOIN students s ON s.id = ar.student_id "
            "WHERE ar.session_id=? "
            "ORDER BY s.last_name, s.first_name",
            (session_id,),
        )
        keys = ["student_id", "enrollment_no", "last_name", "first_name", "status", "note"]
        return [dict(zip(keys, row)) for row in cur.fetchall()]
    finally:
        conn.close()


def delete_session(session_id: int) -> None:
    """Delete an attendance session and all related data.
    
    This will cascade delete:
    - All attendance records for the session
    - All fee invoices for the session
    """
    conn = get_connection()
    try:
        # Delete fee invoices first (due to foreign key constraints)
        conn.execute("DELETE FROM fee_invoices WHERE session_id=?", (session_id,))
        
        # Delete attendance records
        conn.execute("DELETE FROM attendance_records WHERE session_id=?", (session_id,))
        
        # Delete the session itself
        conn.execute("DELETE FROM attendance_sessions WHERE id=?", (session_id,))
        
        conn.commit()
    finally:
        conn.close()


def get_session_info(session_id: int) -> Optional[Dict[str, Any]]:
    """Get information about a specific session"""
    conn = get_connection()
    try:
        cur = conn.execute(
            "SELECT id, class_id, session_date, created_at FROM attendance_sessions WHERE id=?",
            (session_id,),
        )
        row = cur.fetchone()
        if not row:
            return None
        keys = ["id", "class_id", "session_date", "created_at"]
        return dict(zip(keys, row))
    finally:
        conn.close()