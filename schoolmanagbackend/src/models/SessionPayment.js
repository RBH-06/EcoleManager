const pool = require('../config/database');

const SessionPayment = {
  async create(data) {
    const fields = [
      'enrollment_id', 'session_id', 'is_paid', 'payment_date', 
      'payment_amount', 'payment_method', 'transaction_reference', 
      'notes', 'marked_by'
    ];
    const values = fields.map(f => data[f] || null);
    const placeholders = fields.map((_, i) => `$${i + 1}`).join(', ');
    const query = `INSERT INTO session_payments (${fields.join(', ')}) VALUES (${placeholders}) RETURNING *`;
    const res = await pool.query(query, values);
    return res.rows[0];
  },

  async findByEnrollmentAndSession(enrollmentId, sessionId) {
    const res = await pool.query(
      'SELECT * FROM session_payments WHERE enrollment_id = $1 AND session_id = $2',
      [enrollmentId, sessionId]
    );
    return res.rows[0];
  },

  async findByEnrollment(enrollmentId) {
    const res = await pool.query(`
      SELECT sp.*, s.session_number, s.scheduled_date, s.topic
      FROM session_payments sp
      JOIN sessions s ON sp.session_id = s.id
      WHERE sp.enrollment_id = $1
      ORDER BY s.scheduled_date, s.session_number
    `, [enrollmentId]);
    return res.rows;
  },

  async findByStudent(studentId) {
    const res = await pool.query(`
      SELECT sp.*, s.session_number, s.scheduled_date, s.topic,
             e.enrollment_date, tc.name as class_name, t.name as training_name,
             tr.payment_type, tr.price_per_session, tr.price_full
      FROM session_payments sp
      JOIN sessions s ON sp.session_id = s.id
      JOIN enrollments e ON sp.enrollment_id = e.id
      JOIN training_classes tc ON e.class_id = tc.id
      JOIN trainings tr ON tc.training_id = tr.id
      WHERE e.student_id = $1
      ORDER BY s.scheduled_date DESC, s.session_number
    `, [studentId]);
    return res.rows;
  },

  async findBySession(sessionId) {
    const res = await pool.query(`
      SELECT sp.*, e.student_id, s.first_name as student_first_name, s.last_name as student_last_name
      FROM session_payments sp
      JOIN enrollments e ON sp.enrollment_id = e.id
      JOIN students s ON e.student_id = s.id
      WHERE sp.session_id = $1
      ORDER BY s.first_name, s.last_name
    `, [sessionId]);
    return res.rows;
  },

  async updatePaymentStatus(enrollmentId, sessionId, isPaid, paymentData = {}) {
    const existing = await this.findByEnrollmentAndSession(enrollmentId, sessionId);
    
    if (existing) {
      // Update existing record
      const fields = ['is_paid', 'payment_date', 'payment_amount', 'payment_method', 'transaction_reference', 'notes'];
      const values = [isPaid, paymentData.payment_date, paymentData.payment_amount, paymentData.payment_method, paymentData.transaction_reference, paymentData.notes];
      const updates = fields.map((field, index) => `${field} = $${index + 1}`).join(', ');
      const query = `UPDATE session_payments SET ${updates} WHERE enrollment_id = $${fields.length + 1} AND session_id = $${fields.length + 2} RETURNING *`;
      const res = await pool.query(query, [...values, enrollmentId, sessionId]);
      return res.rows[0];
    } else {
      // Create new record
      return await this.create({
        enrollment_id: enrollmentId,
        session_id: sessionId,
        is_paid: isPaid,
        ...paymentData
      });
    }
  },

  async getPaymentSummary(enrollmentId) {
    const res = await pool.query(`
      SELECT 
        COUNT(*) as total_sessions,
        COUNT(CASE WHEN sp.is_paid = true THEN 1 END) as paid_sessions,
        COUNT(CASE WHEN sp.is_paid = false THEN 1 END) as unpaid_sessions,
        SUM(CASE WHEN sp.is_paid = true THEN sp.payment_amount ELSE 0 END) as total_paid_amount
      FROM session_payments sp
      WHERE sp.enrollment_id = $1
    `, [enrollmentId]);
    return res.rows[0];
  },

  async markSessionAsPaid(enrollmentId, sessionId, paymentData = {}) {
    return await this.updatePaymentStatus(enrollmentId, sessionId, true, paymentData);
  },

  async markSessionAsUnpaid(enrollmentId, sessionId) {
    return await this.updatePaymentStatus(enrollmentId, sessionId, false);
  },

  async delete(id) {
    await pool.query('DELETE FROM session_payments WHERE id = $1', [id]);
    return true;
  }
};

module.exports = SessionPayment; 