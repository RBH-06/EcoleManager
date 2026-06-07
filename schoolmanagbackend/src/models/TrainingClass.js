const pool = require('../config/database');

const TrainingClass = {
  async create(data) {
    const fields = [
      'training_id', 'teacher_id', 'name', 'start_date', 'end_date', 'status'
    ];
    const values = fields.map(f => data[f] || null);
    const placeholders = fields.map((_, i) => `$${i + 1}`).join(', ');
    const query = `INSERT INTO training_classes (${fields.join(', ')}) VALUES (${placeholders}) RETURNING *`;
    const res = await pool.query(query, values);
    return res.rows[0];
  },

  async findAll({ page = 1, limit = 10, training_id, teacher_id, status }) {
    let query = `SELECT tc.*, 
      t.name AS training_name, t.description AS training_description, 
      te.first_name AS teacher_first_name, te.last_name AS teacher_last_name, te.email AS teacher_email
      FROM training_classes tc
      LEFT JOIN trainings t ON tc.training_id = t.id
      LEFT JOIN teachers te ON tc.teacher_id = te.id
      WHERE 1=1`;
    const params = [];
    if (training_id) {
      params.push(training_id);
      query += ` AND tc.training_id = $${params.length}`;
    }
    if (teacher_id) {
      params.push(teacher_id);
      query += ` AND tc.teacher_id = $${params.length}`;
    }
    if (status) {
      params.push(status);
      query += ` AND tc.status = $${params.length}`;
    }
    params.push(limit);
    params.push((page - 1) * limit);
    query += ` ORDER BY tc.start_date DESC LIMIT $${params.length - 1} OFFSET $${params.length}`;
    const res = await pool.query(query, params);
    return res.rows.map(row => ({
      id: row.id,
      name: row.name,
      start_date: row.start_date,
      end_date: row.end_date,
      status: row.status,
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
    }));
  },

  async findById(id) {
    const res = await pool.query('SELECT * FROM training_classes WHERE id = $1', [id]);
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
    const query = `UPDATE training_classes SET ${fields.join(', ')}, updated_at = NOW() WHERE id = $${idx} RETURNING *`;
    const res = await pool.query(query, values);
    return res.rows[0];
  },

  async delete(id) {
    await pool.query('DELETE FROM training_classes WHERE id = $1', [id]);
    return true;
  }
};

module.exports = TrainingClass;
