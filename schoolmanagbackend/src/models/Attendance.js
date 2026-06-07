const pool = require('../config/database');

const Attendance = {
  async getBySession(session_id) {
    const res = await pool.query(
      'SELECT * FROM attendance WHERE session_id = $1',
      [session_id]
    );
    return res.rows;
  },

  async bulkUpsert(session_id, attendanceList) {
    // Upsert attendance for each student in the list
    const results = [];
    for (const item of attendanceList) {
      const { student_id, status, notes } = item;
      // Try to update first
      const updateRes = await pool.query(
        `UPDATE attendance SET status = $1, notes = $2, updated_at = NOW()
         WHERE session_id = $3 AND student_id = $4 RETURNING *`,
        [status, notes || null, session_id, student_id]
      );
      if (updateRes.rows.length > 0) {
        results.push(updateRes.rows[0]);
      } else {
        // Insert if not exists
        const insertRes = await pool.query(
          `INSERT INTO attendance (session_id, student_id, status, notes)
           VALUES ($1, $2, $3, $4) RETURNING *`,
          [session_id, student_id, status, notes || null]
        );
        results.push(insertRes.rows[0]);
      }
    }
    return results;
  },

  async upsert(session_id, student_id, status, notes) {
    // Update if exists, else insert
    const updateRes = await pool.query(
      `UPDATE attendance SET status = $1, notes = $2, updated_at = NOW()
       WHERE session_id = $3 AND student_id = $4 RETURNING *`,
      [status, notes || null, session_id, student_id]
    );
    if (updateRes.rows.length > 0) {
      return updateRes.rows[0];
    } else {
      const insertRes = await pool.query(
        `INSERT INTO attendance (session_id, student_id, status, notes)
         VALUES ($1, $2, $3, $4) RETURNING *`,
        [session_id, student_id, status, notes || null]
      );
      return insertRes.rows[0];
    }
  },

  async delete(session_id, student_id) {
    await pool.query(
      'DELETE FROM attendance WHERE session_id = $1 AND student_id = $2',
      [session_id, student_id]
    );
    return true;
  },

  async getSessionAttendanceWithStudents(session_id) {
    // Get the class_id for the session
    const sessionRes = await pool.query('SELECT class_id FROM sessions WHERE id = $1', [session_id]);
    if (!sessionRes.rows.length) return [];
    const class_id = sessionRes.rows[0].class_id;
    // Get all students enrolled in the class, left join with attendance for this session
    const res = await pool.query(`
      SELECT
        s.id AS student_id,
        s.first_name,
        s.last_name,
        a.status,
        a.notes,
        a.updated_at,
        a.created_at
      FROM enrollments e
      JOIN students s ON e.student_id = s.id
      LEFT JOIN attendance a ON a.student_id = s.id AND a.session_id = $1
      WHERE e.class_id = $2
    `, [session_id, class_id]);
    return res.rows;
  }
};

module.exports = Attendance;
