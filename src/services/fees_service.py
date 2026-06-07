from typing import Optional, List, Dict, Any
from db.connection import get_connection

Row = Dict[str, Any]


# --- Fee rules (amount per class session) ---

def set_fee_rule(class_id: int, amount_cents: int, currency: str = "MAD", active: bool = True) -> int:
    """Create or update the active fee rule for a class.

    Uses UPSERT on unique(class_id)
    """
    conn = get_connection()
    try:
        cur = conn.execute(
            """
            INSERT INTO fee_rules(class_id, amount_cents, currency, active)
            VALUES(?,?,?,?)
            ON CONFLICT(class_id) DO UPDATE SET
                amount_cents=excluded.amount_cents,
                currency=excluded.currency,
                active=excluded.active
            """,
            (class_id, amount_cents, currency, 1 if active else 0),
        )
        conn.commit()
        # fetch id
        row = conn.execute("SELECT id FROM fee_rules WHERE class_id=?", (class_id,)).fetchone()
        return int(row[0])
    finally:
        conn.close()


def get_fee_rule(class_id: int) -> Optional[Row]:
    conn = get_connection()
    try:
        cur = conn.execute(
            "SELECT id, class_id, amount_cents, currency, active, created_at FROM fee_rules WHERE class_id=?",
            (class_id,),
        )
        row = cur.fetchone()
        if not row:
            return None
        keys = ["id", "class_id", "amount_cents", "currency", "active", "created_at"]
        rec = dict(zip(keys, row))
        rec["active"] = bool(rec["active"])  # convert int -> bool
        return rec
    finally:
        conn.close()


# --- Invoice generation and payments ---

def generate_invoices_for_session(class_id: int, session_id: int) -> List[int]:
    """Ensure invoices exist for each enrolled student for this session.

    - Requires an active fee rule for the class
    - Creates unpaid invoices for all enrolled students (if not already created)
    - Returns list of created invoice IDs
    """
    conn = get_connection()
    try:
        # find active rule
        rule = conn.execute(
            "SELECT amount_cents, currency FROM fee_rules WHERE class_id=? AND active=1",
            (class_id,),
        ).fetchone()
        if not rule:
            return []  # No rule -> skip silently; UI can warn
        amount_cents, currency = rule

        # enrolled students
        students = conn.execute(
            "SELECT student_id FROM class_enrollments WHERE class_id=?",
            (class_id,),
        ).fetchall()
        created_ids: List[int] = []
        for (student_id,) in students:
            cur = conn.execute(
                """
                INSERT INTO fee_invoices(session_id, student_id, amount_cents, currency, status)
                VALUES(?,?,?,?, 'unpaid')
                ON CONFLICT(session_id, student_id) DO NOTHING
                """,
                (session_id, student_id, amount_cents, currency),
            )
            if cur.rowcount:  # inserted
                created_ids.append(cur.lastrowid)
        conn.commit()
        return created_ids
    finally:
        conn.close()


def list_invoices_for_session(session_id: int) -> List[Row]:
    conn = get_connection()
    try:
        cur = conn.execute(
            """
            SELECT fi.id, fi.session_id, fi.student_id, s.enrollment_no, s.last_name, s.first_name,
                   fi.amount_cents, fi.currency, fi.status, fi.created_at, fi.paid_at
            FROM fee_invoices fi
            JOIN students s ON s.id = fi.student_id
            WHERE fi.session_id=?
            ORDER BY s.last_name, s.first_name
            """,
            (session_id,),
        )
        keys = [
            "id",
            "session_id",
            "student_id",
            "enrollment_no",
            "last_name",
            "first_name",
            "amount_cents",
            "currency",
            "status",
            "created_at",
            "paid_at",
        ]
        return [dict(zip(keys, row)) for row in cur.fetchall()]
    finally:
        conn.close()


def mark_invoice_paid(invoice_id: int, user_id: Optional[int] = None) -> None:
    conn = get_connection()
    try:
        # Get invoice details for logging
        invoice_info = conn.execute(
            """
            SELECT fi.amount_cents, fi.currency, s.enrollment_no, s.first_name, s.last_name,
                   asess.session_date, c.name as class_name
            FROM fee_invoices fi
            JOIN students s ON s.id = fi.student_id
            JOIN attendance_sessions asess ON asess.id = fi.session_id
            JOIN classes c ON c.id = asess.class_id
            WHERE fi.id = ?
            """,
            (invoice_id,)
        ).fetchone()
        
        conn.execute(
            "UPDATE fee_invoices SET status='paid', paid_at=datetime('now') WHERE id=?",
            (invoice_id,),
        )
        conn.commit()
        
        # Log the payment
        if invoice_info:
            amount_cents, currency, enrollment_no, first_name, last_name, session_date, class_name = invoice_info
            amount = amount_cents / 100
            student_name = f"{first_name} {last_name} ({enrollment_no})"
            details = f"Paiement reçu: {student_name}, Montant: {amount} {currency}, Classe: {class_name}, Date: {session_date}"
            
            try:
                from services.log_service import log_action
                log_action("payment_received", user_id=user_id, entity="payment", entity_id=invoice_id, details=details)
            except Exception:
                # Don't fail if logging fails
                pass
                
    finally:
        conn.close()


def mark_invoice_unpaid(invoice_id: int, user_id: Optional[int] = None) -> None:
    conn = get_connection()
    try:
        # Get invoice details for logging
        invoice_info = conn.execute(
            """
            SELECT fi.amount_cents, fi.currency, s.enrollment_no, s.first_name, s.last_name,
                   asess.session_date, c.name as class_name
            FROM fee_invoices fi
            JOIN students s ON s.id = fi.student_id
            JOIN attendance_sessions asess ON asess.id = fi.session_id
            JOIN classes c ON c.id = asess.class_id
            WHERE fi.id = ?
            """,
            (invoice_id,)
        ).fetchone()
        
        conn.execute("UPDATE fee_invoices SET status='unpaid', paid_at=NULL WHERE id=?", (invoice_id,))
        conn.commit()
        
        # Log the payment reversal
        if invoice_info:
            amount_cents, currency, enrollment_no, first_name, last_name, session_date, class_name = invoice_info
            amount = amount_cents / 100
            student_name = f"{first_name} {last_name} ({enrollment_no})"
            details = f"Paiement annulé: {student_name}, Montant: {amount} {currency}, Classe: {class_name}, Date: {session_date}"
            
            try:
                from services.log_service import log_action
                log_action("payment_cancelled", user_id=user_id, entity="payment", entity_id=invoice_id, details=details)
            except Exception:
                # Don't fail if logging fails
                pass
                
    finally:
        conn.close()


def list_invoices_with_attendance(session_id: int) -> List[Row]:
    """Get invoice data combined with attendance status for a session"""
    conn = get_connection()
    try:
        cur = conn.execute(
            """
            SELECT fi.id, fi.session_id, fi.student_id, s.enrollment_no, s.last_name, s.first_name,
                   fi.amount_cents, fi.currency, fi.status as payment_status, fi.created_at, fi.paid_at,
                   COALESCE(ar.status, 'Unknown') as attendance_status,
                   COALESCE(ar.note, '') as attendance_note
            FROM fee_invoices fi
            JOIN students s ON s.id = fi.student_id
            LEFT JOIN attendance_records ar ON ar.session_id = fi.session_id AND ar.student_id = fi.student_id
            WHERE fi.session_id=?
            ORDER BY s.last_name, s.first_name
            """,
            (session_id,),
        )
        keys = [
            "id",
            "session_id", 
            "student_id",
            "enrollment_no",
            "last_name",
            "first_name", 
            "amount_cents",
            "currency",
            "payment_status",
            "created_at",
            "paid_at",
            "attendance_status",
            "attendance_note"
        ]
        return [dict(zip(keys, row)) for row in cur.fetchall()]
    finally:
        conn.close()


def list_unpaid_invoices_by_class(class_id: int) -> List[Row]:
    """List all unpaid invoices for all sessions of a given class, with session date and attendance.
    Useful to show students who didn't pay, aggregated by class.
    """
    conn = get_connection()
    try:
        cur = conn.execute(
            """
            SELECT fi.id, fi.session_id, asess.session_date, fi.student_id,
                   s.enrollment_no, s.last_name, s.first_name,
                   fi.amount_cents, fi.currency, fi.status as payment_status,
                   COALESCE(ar.status, 'Unknown') as attendance_status
            FROM fee_invoices fi
            JOIN attendance_sessions asess ON asess.id = fi.session_id
            JOIN students s ON s.id = fi.student_id
            LEFT JOIN attendance_records ar ON ar.session_id = fi.session_id AND ar.student_id = fi.student_id
            WHERE asess.class_id = ? AND fi.status = 'unpaid'
            ORDER BY asess.session_date DESC, s.last_name, s.first_name
            """,
            (class_id,),
        )
        keys = [
            "id", "session_id", "session_date", "student_id",
            "enrollment_no", "last_name", "first_name",
            "amount_cents", "currency", "payment_status", "attendance_status"
        ]
        return [dict(zip(keys, row)) for row in cur.fetchall()]
    finally:
        conn.close()