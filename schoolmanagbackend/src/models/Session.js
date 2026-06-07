const pool = require('../config/database');

const Session = {
  async create(data) {
    const fields = [
      'class_id', 'session_number', 'date', 'start_time', 'end_time',
      'topic', 'notes'
    ];
    const values = fields.map(f => data[f] || null);
    const placeholders = fields.map((_, i) => `$${i + 1}`).join(', ');
    const query = `INSERT INTO sessions (${fields.join(', ')}) VALUES (${placeholders}) RETURNING *`;
    const res = await pool.query(query, values);
    return res.rows[0];
  },

  async findAll({ page = 1, limit = 10, class_id }) {
    let query = 'SELECT * FROM sessions WHERE 1=1';
    const params = [];
    if (class_id) {
      params.push(class_id);
      query += ` AND class_id = $${params.length}`;
    }
    params.push(limit);
    params.push((page - 1) * limit);
    query += ` ORDER BY date DESC, start_time DESC LIMIT $${params.length - 1} OFFSET $${params.length}`;
    const res = await pool.query(query, params);
    return res.rows;
  },

  async findById(id) {
    const res = await pool.query('SELECT * FROM sessions WHERE id = $1', [id]);
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
    const query = `UPDATE sessions SET ${fields.join(', ')}, updated_at = NOW() WHERE id = $${idx} RETURNING *`;
    const res = await pool.query(query, values);
    return res.rows[0];
  },

  async delete(id) {
    await pool.query('DELETE FROM sessions WHERE id = $1', [id]);
    return true;
  }
};

module.exports = Session;
