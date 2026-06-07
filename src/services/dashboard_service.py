from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from db.connection import get_connection


def get_dashboard_statistics() -> Dict[str, Any]:
    """Get comprehensive dashboard statistics"""
    conn = get_connection()
    try:
        stats = {}
        
        # Total counts
        stats['total_students'] = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
        stats['total_classes'] = conn.execute("SELECT COUNT(*) FROM classes").fetchone()[0] 
        stats['total_users'] = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        stats['total_sessions'] = conn.execute("SELECT COUNT(*) FROM attendance_sessions").fetchone()[0]
        
        # Gender distribution
        gender_stats = conn.execute(
            "SELECT gender, COUNT(*) FROM students GROUP BY gender"
        ).fetchall()
        stats['gender_distribution'] = {row[0]: row[1] for row in gender_stats}
        
        # Payment statistics
        payment_stats = conn.execute(
            "SELECT status, COUNT(*) FROM fee_invoices GROUP BY status"
        ).fetchall() 
        stats['payment_distribution'] = {row[0]: row[1] for row in payment_stats}
        
        # Recent activity (last 7 days)
        seven_days_ago = (datetime.now() - timedelta(days=7)).isoformat()
        
        stats['recent_students'] = conn.execute(
            "SELECT COUNT(*) FROM students WHERE created_at >= ?", 
            (seven_days_ago,)
        ).fetchone()[0]
        
        stats['recent_sessions'] = conn.execute(
            "SELECT COUNT(*) FROM attendance_sessions WHERE created_at >= ?",
            (seven_days_ago,)
        ).fetchone()[0]
        
        stats['recent_payments'] = conn.execute(
            "SELECT COUNT(*) FROM fee_invoices WHERE paid_at >= ?",
            (seven_days_ago,)
        ).fetchone()[0]
        
        # Top classes by enrollment
        stats['top_classes'] = conn.execute(
            """
            SELECT c.name, c.level, COUNT(ce.student_id) as enrollment_count
            FROM classes c
            LEFT JOIN class_enrollments ce ON c.id = ce.class_id
            GROUP BY c.id, c.name, c.level
            ORDER BY enrollment_count DESC
            LIMIT 5
            """
        ).fetchall()
        
        # Attendance rates (last 30 days)
        thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
        attendance_rates = conn.execute(
            """
            SELECT ar.status, COUNT(*) as count
            FROM attendance_records ar
            JOIN attendance_sessions s ON ar.session_id = s.id
            WHERE s.created_at >= ?
            GROUP BY ar.status
            """,
            (thirty_days_ago,)
        ).fetchall()
        stats['attendance_rates'] = {row[0]: row[1] for row in attendance_rates}
        
        return stats
    finally:
        conn.close()


def get_recent_activity(limit: int = 10) -> List[Dict[str, Any]]:
    """Get comprehensive recent system activity"""
    conn = get_connection()
    try:
        all_activities = []
        
        # 1. 👥 Student Activities
        student_activities = conn.execute(
            """
            SELECT 'student_new' as type, 
                   first_name || ' ' || last_name as name, 
                   created_at, 
                   '👥 Nouvel élève: ' || first_name || ' ' || last_name as action,
                   'high' as priority
            FROM students 
            ORDER BY created_at DESC 
            LIMIT ?
            """,
            (limit//4,)
        ).fetchall()
        
        # 2. 📚 Class Activities  
        class_activities = conn.execute(
            """
            SELECT 'class_new' as type,
                   name as name,
                   created_at,
                   '📚 Nouvelle classe: ' || name || ' (' || level || ')' as action,
                   'medium' as priority
            FROM classes
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit//4,)
        ).fetchall()
        
        # 3. 📝 Attendance Activities
        session_activities = conn.execute(
            """
            SELECT 'session_new' as type, 
                   c.name as name, 
                   s.created_at,
                   '📝 Séance créée: ' || c.name || ' (' || date(s.session_date) || ')' as action,
                   'medium' as priority
            FROM attendance_sessions s
            JOIN classes c ON s.class_id = c.id
            ORDER BY s.created_at DESC
            LIMIT ?
            """,
            (limit//4,)
        ).fetchall()
        
        # 4. 💰 Payment Activities (recent payments)
        payment_activities = conn.execute(
            """
            SELECT 'payment_received' as type,
                   s.first_name || ' ' || s.last_name as name,
                   fi.paid_at as timestamp,
                   '💰 Paiement reçu: ' || s.first_name || ' ' || s.last_name || 
                   ' (' || (fi.amount_cents/100.0) || ' ' || fi.currency || ')' as action,
                   'high' as priority
            FROM fee_invoices fi
            JOIN students s ON fi.student_id = s.id
            WHERE fi.status = 'paid' AND fi.paid_at IS NOT NULL
            ORDER BY fi.paid_at DESC
            LIMIT ?
            """,
            (limit//4,)
        ).fetchall()
        
        # 5. 👤 User Management Activities
        user_activities = conn.execute(
            """
            SELECT 'user_new' as type,
                   u.username as name,
                   u.created_at as timestamp,
                   '👤 Nouvel utilisateur: ' || u.username || ' (' || r.name || ')' as action,
                   'low' as priority
            FROM users u
            JOIN roles r ON u.role_id = r.id
            WHERE u.created_at >= datetime('now', '-7 days')
            ORDER BY u.created_at DESC
            LIMIT ?
            """,
            (limit//4,)
        ).fetchall()
        
        # 6. 📊 Class Enrollment Activities
        enrollment_activities = conn.execute(
            """
            SELECT 'enrollment_new' as type,
                   s.first_name || ' ' || s.last_name as name,
                   ce.created_at as timestamp,
                   '📊 Inscription: ' || s.first_name || ' ' || s.last_name || 
                   ' → ' || c.name as action,
                   'medium' as priority
            FROM class_enrollments ce
            JOIN students s ON ce.student_id = s.id
            JOIN classes c ON ce.class_id = c.id
            WHERE ce.created_at IS NOT NULL
            ORDER BY ce.created_at DESC
            LIMIT ?
            """,
            (limit//4,)
        ).fetchall()
        
        # Combine all activities
        for activity_set in [student_activities, class_activities, session_activities, 
                           payment_activities, user_activities, enrollment_activities]:
            for row in activity_set:
                all_activities.append({
                    'type': row[0],
                    'name': row[1],
                    'timestamp': row[2] or datetime.now().isoformat(),
                    'action': row[3],
                    'priority': row[4]
                })
        
        # Sort by timestamp and limit
        activities = sorted(all_activities, key=lambda x: x['timestamp'], reverse=True)[:limit]
        
        return activities
    finally:
        conn.close()


def get_upcoming_tasks() -> List[Dict[str, Any]]:
    """Get upcoming tasks or reminders"""
    # This is a placeholder for future task management features
    tasks = [
        {
            'title': 'Révision des paiements en retard',
            'description': 'Vérifier les élèves avec des paiements en souffrance',
            'priority': 'high',
            'icon': '💰'
        },
        {
            'title': 'Rapport mensuel d\'assiduité', 
            'description': 'Générer le rapport d\'assiduité du mois',
            'priority': 'medium',
            'icon': '📊'
        },
        {
            'title': 'Mise à jour des informations des élèves',
            'description': 'Vérifier et mettre à jour les contacts parents',
            'priority': 'low', 
            'icon': '👥'
        }
    ]
    return tasks


def get_system_health() -> Dict[str, Any]:
    """Get system health indicators"""
    conn = get_connection()
    try:
        health = {
            'database_status': 'healthy',
            'total_records': 0,
            'last_backup': 'Non configuré',
            'active_sessions': 0
        }
        
        # Count total records across main tables
        tables = ['students', 'classes', 'users', 'attendance_sessions', 'fee_invoices']
        total = 0
        for table in tables:
            count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            total += count
            
        health['total_records'] = total
        health['database_status'] = 'healthy' if total > 0 else 'warning'
        
        # Count recent activity (last 24h) as "active sessions"
        yesterday = (datetime.now() - timedelta(days=1)).isoformat()
        health['active_sessions'] = conn.execute(
            "SELECT COUNT(*) FROM attendance_sessions WHERE created_at >= ?",
            (yesterday,)
        ).fetchone()[0]
        
        return health
    finally:
        conn.close()