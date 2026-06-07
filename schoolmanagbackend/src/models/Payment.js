const pool = require('../config/database');

const Payment = {
  async create(data) {
    const fields = [
      'enrollment_id', 'amount', 'payment_method', 'payment_date', 'due_date',
      'status', 'transaction_reference', 'notes', 'created_by'
    ];
    const values = fields.map(f => data[f] || null);
    const placeholders = fields.map((_, i) => `$${i + 1}`).join(', ');
    const query = `INSERT INTO payments (${fields.join(', ')}) VALUES (${placeholders}) RETURNING *`;
    const res = await pool.query(query, values);
    return res.rows[0];
  },

  async findAll({ page = 1, limit = 10, enrollment_id, student_id, status, payment_date }) {
    let query = 'SELECT * FROM payments WHERE 1=1';
    const params = [];
    if (enrollment_id) {
      params.push(enrollment_id);
      query += ` AND enrollment_id = $${params.length}`;
    }
    if (student_id) {
      params.push(student_id);
      query += ` AND enrollment_id IN (SELECT id FROM enrollments WHERE student_id = $${params.length})`;
    }
    if (status) {
      params.push(status);
      query += ` AND status = $${params.length}`;
    }
    if (payment_date) {
      params.push(payment_date);
      query += ` AND payment_date = $${params.length}`;
    }
    params.push(limit);
    params.push((page - 1) * limit);
    query += ` ORDER BY payment_date DESC LIMIT $${params.length - 1} OFFSET $${params.length}`;
    const res = await pool.query(query, params);
    return res.rows;
  },

  async findById(id) {
    const res = await pool.query('SELECT * FROM payments WHERE id = $1', [id]);
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
    const query = `UPDATE payments SET ${fields.join(', ')}, updated_at = NOW() WHERE id = $${idx} RETURNING *`;
    const res = await pool.query(query, values);
    return res.rows[0];
  },

  async delete(id) {
    await pool.query('DELETE FROM payments WHERE id = $1', [id]);
    return true;
  },

  async getStudentPayments(studentId, startDate, endDate) {
    const res = await pool.query(
      `SELECT * FROM payments WHERE enrollment_id IN (SELECT id FROM enrollments WHERE student_id = $1)
       AND payment_date BETWEEN $2 AND $3`,
      [studentId, startDate, endDate]
    );
    return res.rows;
  },

  async getOutstandingPayments() {
    const res = await pool.query(
      `SELECT * FROM payments WHERE status = 'pending' AND due_date < CURRENT_DATE`
    );
    return res.rows;
  }
};

module.exports = Payment;
