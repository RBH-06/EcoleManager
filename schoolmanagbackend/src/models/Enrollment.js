const pool = require('../config/database');

const Enrollment = {
  async create(data) {
    const fields = [
      'student_id', 'class_id', 'enrollment_date', 'status'
    ];
    const values = fields.map(f => data[f] || null);
    const placeholders = fields.map((_, i) => `$${i + 1}`).join(', ');
    const query = `INSERT INTO enrollments (${fields.join(', ')}) VALUES (${placeholders}) RETURNING *`;
    const res = await pool.query(query, values);
    return res.rows[0];
  },
  async findByIdWithDetails(id) {
    const res = await pool.query(`
      SELECT e.*, 
        s.first_name AS student_first_name, s.last_name AS student_last_name, s.email AS student_email, s.phone AS student_phone,
        s.registration_date AS student_registration_date, s.bday AS student_bday, s.parentname AS student_parentname, s.parentphone AS student_parentphone,
        c.name AS class_name, c.start_date AS class_start_date, c.end_date AS class_end_date, c.status AS class_status,
        t.id AS training_id, t.name AS training_name, t.description AS training_description,
        te.id AS teacher_id, te.first_name AS teacher_first_name, te.last_name AS teacher_last_name, te.email AS teacher_email
      FROM enrollments e
      LEFT JOIN students s ON e.student_id = s.id
      LEFT JOIN training_classes c ON e.class_id = c.id
      LEFT JOIN trainings t ON c.training_id = t.id
      LEFT JOIN teachers te ON c.teacher_id = te.id
      WHERE e.id = $1
    `, [id]);
    const row = res.rows[0];
    if (!row) return null;
    return {
      id: row.id,
      enrollment_date: row.enrollment_date,
      status: row.status,
      created_at: row.created_at,
      student: {
        id: row.student_id,
        first_name: row.student_first_name,
        last_name: row.student_last_name,
        email: row.student_email,
        phone: row.student_phone,
        registration_date: row.student_registration_date,
        bday: row.student_bday,
        parentname: row.student_parentname,
        parentphone: row.student_parentphone
      },
      class: {
        id: row.class_id,
        name: row.class_name,
        start_date: row.class_start_date,
        end_date: row.class_end_date,
        status: row.class_status,
        training: {
          id: row.training_id,
          name: row.training_name,
          description: row.training_description
        },
        teacher: {
          id: row.teacher_id,
          first_name: row.teacher_first_name,
          last_name: row.teacher_last_name,
          email: row.teacher_email
        }
      }
    };
  },

  async findAllWithDetails({ page = 1, limit = 10, student_id, class_id, status }) {
    let query = `SELECT e.*, 
        s.first_name AS student_first_name, s.last_name AS student_last_name, s.email AS student_email, s.phone AS student_phone,
        s.registration_date AS student_registration_date, s.bday AS student_bday, s.parentname AS student_parentname, s.parentphone AS student_parentphone,
        c.name AS class_name, c.start_date AS class_start_date, c.end_date AS class_end_date, c.status AS class_status,
        t.id AS training_id, t.name AS training_name, t.description AS training_description,
        te.id AS teacher_id, te.first_name AS teacher_first_name, te.last_name AS teacher_last_name, te.email AS teacher_email
      FROM enrollments e
      LEFT JOIN students s ON e.student_id = s.id
      LEFT JOIN training_classes c ON e.class_id = c.id
      LEFT JOIN trainings t ON c.training_id = t.id
      LEFT JOIN teachers te ON c.teacher_id = te.id
      WHERE 1=1`;
    const params = [];
    if (student_id) {
      params.push(student_id);
      query += ` AND e.student_id = $${params.length}`;
    }
    if (class_id) {
      params.push(class_id);
      query += ` AND e.class_id = $${params.length}`;
    }
    if (status) {
      params.push(status);
      query += ` AND e.status = $${params.length}`;
    }
    params.push(limit);
    params.push((page - 1) * limit);
    query += ` ORDER BY e.enrollment_date DESC LIMIT $${params.length - 1} OFFSET $${params.length}`;
    const res = await pool.query(query, params);
    return res.rows.map(row => ({
      id: row.id,
      enrollment_date: row.enrollment_date,
      status: row.status,
      created_at: row.created_at,
      student: {
        id: row.student_id,
        first_name: row.student_first_name,
        last_name: row.student_last_name,
        email: row.student_email,
        phone: row.student_phone,
        registration_date: row.student_registration_date,
        bday: row.student_bday,
        parentname: row.student_parentname,
        parentphone: row.student_parentphone
      },
      class: {
        id: row.class_id,
        name: row.class_name,
        start_date: row.class_start_date,
        end_date: row.class_end_date,
        status: row.class_status,
        training: {
          id: row.training_id,
          name: row.training_name,
          description: row.training_description
        },
        teacher: {
          id: row.teacher_id,
          first_name: row.teacher_first_name,
          last_name: row.teacher_last_name,
          email: row.teacher_email
        }
      }
    }));
  },

  async findAll({ page = 1, limit = 10, student_id, class_id, status }) {
    let query = 'SELECT * FROM enrollments WHERE 1=1';
    const params = [];
    if (student_id) {
      params.push(student_id);
      query += ` AND student_id = $${params.length}`;
    }
    if (class_id) {
      params.push(class_id);
      query += ` AND class_id = $${params.length}`;
    }
    if (status) {
      params.push(status);
      query += ` AND status = $${params.length}`;
    }
    params.push(limit);
    params.push((page - 1) * limit);
    query += ` ORDER BY enrollment_date DESC LIMIT $${params.length - 1} OFFSET $${params.length}`;
    const res = await pool.query(query, params);
    return res.rows;
  },

  async findById(id) {
    const res = await pool.query('SELECT * FROM enrollments WHERE id = $1', [id]);
    return res.rows[0];
  },

  async update(id, data) {
    const fields = [];
    const values = [];
    let idx = 1;
    for (const key in data) {
      fields.push(`${key} = $${idx++}`);
      values.push(data[key]);
    }
    values.push(id);
    const query = `UPDATE enrollments SET ${fields.join(', ')}, updated_at = NOW() WHERE id = $${idx} RETURNING *`;
    const res = await pool.query(query, values);
    return res.rows[0];
  },

  async delete(id) {
    await pool.query('DELETE FROM enrollments WHERE id = $1', [id]);
    return true;
  },

  // Removed incrementSessionUsage as sessions_used is no longer present
};

module.exports = Enrollment;
