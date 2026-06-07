from typing import Optional, Dict, Any, List
from db.connection import get_connection

# Actions examples: student_create, student_update, student_delete, class_create, user_login, etc.

def log_action(action: str, user_id: Optional[int] = None, entity: Optional[str] = None,
               entity_id: Optional[int] = None, details: Optional[str] = None) -> None:
    """Insert an audit log entry."""
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO logs(user_id, action, entity, entity_id, details) VALUES (?,?,?,?,?)",
            (user_id, action, entity, entity_id, details),
        )
        conn.commit()
    finally:
        conn.close()


def list_logs(limit: int = 200, offset: int = 0, user_id: Optional[int] = None,
              action_like: Optional[str] = None) -> List[Dict[str, Any]]:
    """List logs with optional filters."""
    sql = [
        "SELECT l.id, l.timestamp, l.user_id, u.username, l.action, l.entity, l.entity_id, l.details ",
        "FROM logs l LEFT JOIN users u ON u.id = l.user_id",
        "WHERE 1=1",
    ]
    params: list = []
    if user_id is not None:
        sql.append("AND l.user_id = ?")
        params.append(user_id)
    if action_like:
        sql.append("AND l.action LIKE ?")
        params.append(f"%{action_like}%")
    sql.append("ORDER BY l.timestamp DESC, l.id DESC LIMIT ? OFFSET ?")
    params.extend([limit, offset])

    conn = get_connection()
    try:
        cur = conn.execute("\n".join(sql), tuple(params))
        keys = ["id", "timestamp", "user_id", "username", "action", "entity", "entity_id", "details"]
        return [dict(zip(keys, row)) for row in cur.fetchall()]
    finally:
        conn.close()