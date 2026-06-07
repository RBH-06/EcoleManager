const pool = require('../config/database');

const Student = {
  async create(data) {
    const fields = [
      'first_name', 'last_name', 'email', 'phone', 'registration_date', 'notes', 'bday', 'parentname', 'parentphone'
    ];
    const values = fields.map(f => data[f] || null);
    const placeholders = fields.map((_, i) => `$${i + 1}`).join(', ');
    const query = `INSERT INTO students (${fields.join(', ')}) VALUES (${placeholders}) RETURNING *`;
    const res = await pool.query(query, values);
    return res.rows[0];
  },

  async findAll({ page = 1, limit = 10, search, status }) {
    let query = 'SELECT id, first_name, last_name, email, phone, registration_date, notes, bday, parentname, parentphone FROM students WHERE 1=1';
    const params = [];
    if (search) {
      params.push(`%${search}%`);
      query += ` AND (first_name ILIKE $${params.length} OR last_name ILIKE $${params.length} OR email ILIKE $${params.length})`;
    }
    params.push(limit);
    params.push((page - 1) * limit);
    query += ` ORDER BY registration_date DESC LIMIT $${params.length - 1} OFFSET $${params.length}`;
    const res = await pool.query(query, params);
    return res.rows;
  },

  async findById(id) {
    const res = await pool.query('SELECT id, first_name, last_name, email, phone, registration_date, notes, bday, parentname, parentphone FROM students WHERE id = $1', [id]);
    return res.rows[0];
  },

  async update(id, data) {
    const allowedFields = ['first_name', 'last_name', 'email', 'phone', 'registration_date', 'notes', 'bday', 'parentname', 'parentphone'];
    const fields = [];
    const values = [];
    let idx = 1;
    for (const key in data) {
      if (allowedFields.includes(key)) {
        fields.push(`${key} = $${idx++}`);
        values.push(data[key]);
      }
    }
    values.push(id);
    const query = `UPDATE students SET ${fields.join(', ')} WHERE id = $${idx} RETURNING *`;
    const res = await pool.query(query, values);
    return res.rows[0];
  },

  async delete(id) {
    await pool.query('DELETE FROM students WHERE id = $1', [id]);
    return true;
  },

  async findByIdWithEnrollments(id) {
    const studentRes = await pool.query('SELECT id, first_name, last_name, email, phone, registration_date, notes, bday, parentname, parentphone FROM students WHERE id = $1', [id]);
    const student = studentRes.rows[0];
    if (!student) return null;
    const enrollmentsRes = await pool.query('SELECT * FROM enrollments WHERE student_id = $1', [id]);
    student.enrollments = enrollmentsRes.rows;
    return student;
  }
};

module.exports = Student;
