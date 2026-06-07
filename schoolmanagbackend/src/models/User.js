const pool = require('../config/database');

const User = {
  async findById(id) {
    const res = await pool.query('SELECT * FROM users WHERE id = $1', [id]);
    return res.rows[0];
  },

  async findAll({ page = 1, limit = 10, search, role, status }) {
    let query = 'SELECT * FROM users WHERE 1=1';
    const params = [];
    if (search) {
      params.push(`%${search}%`);
      query += ` AND (email ILIKE $${params.length} OR first_name ILIKE $${params.length} OR last_name ILIKE $${params.length})`;
    }
    if (role) {
      params.push(role);
      query += ` AND role = $${params.length}`;
    }
    if (status) {
      params.push(status);
      query += ` AND status = $${params.length}`;
    }
    params.push(limit);
    params.push((page - 1) * limit);
    query += ` ORDER BY created_at DESC LIMIT $${params.length - 1} OFFSET $${params.length}`;
    const res = await pool.query(query, params);
    return res.rows;
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
    const query = `UPDATE users SET ${fields.join(', ')}, updated_at = NOW() WHERE id = $${idx} RETURNING *`;
    const res = await pool.query(query, values);
    return res.rows[0];
  },

  async delete(id) {
    await pool.query('DELETE FROM users WHERE id = $1', [id]);
    return true;
  },

  async hasPermission(userId, permission) {
    const userRes = await pool.query('SELECT * FROM users WHERE id = $1', [userId]);
    const user = userRes.rows[0];
    if (!user) return false;
    if (user.role === 'admin') return true;
    if (user.role === 'sub_admin') {
      const permRes = await pool.query(
        'SELECT * FROM sub_admin_permissions WHERE user_id = $1 AND permission = $2',
        [userId, permission]
      );
      return permRes.rows.length > 0;
    }
    return false;
  }
};

module.exports = User;
