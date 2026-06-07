const pool = require('../config/database');

const Training = {
  async create(data) {
    // Require the correct price field based on paymentpolicy
    if (data.paymentpolicy === 'per session' && !data.price_per_session) {
      throw new Error('price_per_session is required when paymentpolicy is per session');
    }
    if (data.paymentpolicy === 'at once' && !data.total_price) {
      throw new Error('total_price is required when paymentpolicy is at once');
    }
    const fields = [
      'name', 'description', 'total_sessions', 'price_per_session', 'total_price', 'max_students', 'paymentpolicy'
    ];
    const values = fields.map(f => data[f] || null);
    const placeholders = fields.map((_, i) => `$${i + 1}`).join(', ');
    const query = `INSERT INTO trainings (${fields.join(', ')}) VALUES (${placeholders}) RETURNING *`;
    const res = await pool.query(query, values);
    return res.rows[0];
  },

  async findAll({ page = 1, limit = 10 }) {
    let query = 'SELECT * FROM trainings WHERE 1=1';
    const params = [];
    params.push(limit);
    params.push((page - 1) * limit);
    query += ` ORDER BY created_at DESC LIMIT $${params.length - 1} OFFSET $${params.length}`;
    const res = await pool.query(query, params);
    return res.rows;
  },

  async findById(id) {
    const res = await pool.query('SELECT * FROM trainings WHERE id = $1', [id]);
    return res.rows[0];
  },

  async update(id, data) {
    const allowedFields = ['name', 'description', 'total_sessions', 'price_per_session', 'total_price', 'max_students', 'paymentpolicy'];
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
    const query = `UPDATE trainings SET ${fields.join(', ')}, updated_at = NOW() WHERE id = $${idx} RETURNING *`;
    const res = await pool.query(query, values);
    return res.rows[0];
  },

  async delete(id) {
    await pool.query('DELETE FROM trainings WHERE id = $1', [id]);
    return true;
  }
};

module.exports = Training;
