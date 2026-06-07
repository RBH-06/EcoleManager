import sqlite3
from typing import Optional, Tuple, List, Dict

from db.connection import get_connection
from utils.security import hash_password, verify_password


class AuthError(Exception):
    pass


User = Dict[str, object]
Role = Dict[str, object]


def get_role_id_by_name(role_name: str) -> Optional[int]:
    conn = get_connection()
    try:
        cur = conn.execute("SELECT id FROM roles WHERE name = ?", (role_name,))
        row = cur.fetchone()
        return row[0] if row else None
    finally:
        conn.close()


def list_roles() -> List[Role]:
    conn = get_connection()
    try:
        cur = conn.execute("SELECT id, name FROM roles ORDER BY name")
        return [{"id": r[0], "name": r[1]} for r in cur.fetchall()]
    finally:
        conn.close()


def ensure_admin_user(username: str, password: str) -> None:
    conn = get_connection()
    try:
        role_id = get_role_id_by_name("Admin")
        if role_id is None:
            raise AuthError("Le rôle Admin est introuvable.")

        # If the username already exists, ensure it has Admin role
        cur = conn.execute("SELECT id FROM users WHERE username=?", (username,))
        row = cur.fetchone()
        if row:
            conn.execute("UPDATE users SET role_id=? WHERE id=?", (role_id, row[0]))
            conn.commit()
            return

        # Otherwise, if any Admin exists, do nothing
        cur = conn.execute(
            "SELECT u.id FROM users u JOIN roles r ON u.role_id = r.id WHERE r.name = ? LIMIT 1",
            ("Admin",),
        )
        if cur.fetchone():
            return

        # Create admin user
        pwd_hash, salt = hash_password(password)
        conn.execute(
            "INSERT INTO users(username, password_hash, salt, role_id) VALUES (?, ?, ?, ?)",
            (username, pwd_hash, salt, role_id),
        )
        conn.commit()
    finally:
        conn.close()


def authenticate(username: str, password: str) -> Tuple[int, str, Optional[Dict[str, int]]]:
    """Return (user_id, role_name, permissions) if success, else raise AuthError."""
    conn = get_connection()
    try:
        cur = conn.execute(
            "SELECT u.id, u.password_hash, u.salt, r.name FROM users u JOIN roles r ON u.role_id = r.id WHERE u.username = ?",
            (username,),
        )
        row = cur.fetchone()
        if not row:
            raise AuthError("Nom d'utilisateur ou mot de passe invalide.")
        user_id, pwd_hash, salt, role_name = row
        if not verify_password(password, pwd_hash, salt):
            raise AuthError("Nom d'utilisateur ou mot de passe invalide.")

        # Fetch permissions if the user is a subadmin
        permissions = None
        if role_name == "Subadmin":
            cur = conn.execute(
                "SELECT can_manage_students, can_manage_classes, can_manage_attendance, can_manage_fees, can_manage_users "
                "FROM permissions WHERE user_id = ?",
                (user_id,),
            )
            perm_row = cur.fetchone()
            if perm_row:
                permissions = {
                    "can_manage_students": perm_row[0],
                    "can_manage_classes": perm_row[1],
                    "can_manage_attendance": perm_row[2],
                    "can_manage_fees": perm_row[3],
                    "can_manage_users": perm_row[4],
                }
        elif role_name == "Admin":
            # Grant full permissions to admins
            permissions = {
                "can_manage_students": 1,
                "can_manage_classes": 1,
                "can_manage_attendance": 1,
                "can_manage_fees": 1,
                "can_manage_users": 1,
            }

        return user_id, role_name, permissions
    finally:
        conn.close()


def list_users(query: str = "") -> List[User]:
    like = f"%{query}%"
    conn = get_connection()
    try:
        cur = conn.execute(
            "SELECT u.id, u.username, r.name, p.can_manage_students, p.can_manage_classes, p.can_manage_attendance, p.can_manage_fees, p.can_manage_users "
            "FROM users u JOIN roles r ON u.role_id = r.id "
            "LEFT JOIN permissions p ON p.user_id = u.id "
            "WHERE u.username LIKE ? ORDER BY u.username",
            (like,),
        )
        cols = [
            "id", "username", "role",
            "can_manage_students", "can_manage_classes", "can_manage_attendance", "can_manage_fees", "can_manage_users"
        ]
        return [dict(zip(cols, row)) for row in cur.fetchall()]
    finally:
        conn.close()


def get_user(user_id: int) -> Optional[User]:
    conn = get_connection()
    try:
        cur = conn.execute(
            "SELECT u.id, u.username, r.name, u.role_id FROM users u JOIN roles r ON u.role_id = r.id WHERE u.id=?",
            (user_id,),
        )
        row = cur.fetchone()
        if not row:
            return None
        return {"id": row[0], "username": row[1], "role": row[2], "role_id": row[3]}
    finally:
        conn.close()


def create_user(username: str, password: str, role_id: int, permissions: Optional[Dict[str, int]] = None) -> int:
    pwd_hash, salt = hash_password(password)
    conn = get_connection()
    try:
        cur = conn.execute(
            "INSERT INTO users(username, password_hash, salt, role_id) VALUES (?,?,?,?)",
            (username, pwd_hash, salt, role_id),
        )
        user_id = cur.lastrowid
        # Initialize permissions row if provided (only meaningful for Subadmin)
        if permissions:
            conn.execute(
                "INSERT OR REPLACE INTO permissions(user_id, can_manage_students, can_manage_classes, can_manage_attendance, can_manage_fees, can_manage_users) "
                "VALUES(?,?,?,?,?,?)",
                (
                    user_id,
                    int(bool(permissions.get("can_manage_students"))),
                    int(bool(permissions.get("can_manage_classes"))),
                    int(bool(permissions.get("can_manage_attendance"))),
                    int(bool(permissions.get("can_manage_fees"))),
                    int(bool(permissions.get("can_manage_users"))),
                ),
            )
        conn.commit()
        return user_id
    finally:
        conn.close()


def update_user_role(user_id: int, role_id: int, permissions: Optional[Dict[str, int]] = None) -> None:
    conn = get_connection()
    try:
        conn.execute("UPDATE users SET role_id=? WHERE id=?", (role_id, user_id))
        # Update permissions if provided
        if permissions is not None:
            conn.execute(
                "INSERT OR REPLACE INTO permissions(user_id, can_manage_students, can_manage_classes, can_manage_attendance, can_manage_fees, can_manage_users) "
                "VALUES(?,?,?,?,?,?)",
                (
                    user_id,
                    int(bool(permissions.get("can_manage_students"))),
                    int(bool(permissions.get("can_manage_classes"))),
                    int(bool(permissions.get("can_manage_attendance"))),
                    int(bool(permissions.get("can_manage_fees"))),
                    int(bool(permissions.get("can_manage_users"))),
                ),
            )
        conn.commit()
    finally:
        conn.close()


def reset_user_password(user_id: int, new_password: str) -> None:
    pwd_hash, salt = hash_password(new_password)
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE users SET password_hash=?, salt=? WHERE id=?",
            (pwd_hash, salt, user_id),
        )
        conn.commit()
    finally:
        conn.close()


def is_last_admin(user_id: int) -> bool:
    """Return True if removing this user would leave zero admins."""
    conn = get_connection()
    try:
        # Count admins excluding this user
        cur = conn.execute(
            "SELECT COUNT(*) FROM users u JOIN roles r ON u.role_id = r.id WHERE r.name='Admin' AND u.id <> ?",
            (user_id,),
        )
        (count_other_admins,) = cur.fetchone()
        return count_other_admins == 0
    finally:
        conn.close()


def delete_user(user_id: int) -> None:
    if is_last_admin(user_id):
        raise AuthError("Impossible de supprimer le dernier administrateur.")
    conn = get_connection()
    try:
        conn.execute("DELETE FROM users WHERE id=?", (user_id,))
        conn.commit()
    finally:
        conn.close()