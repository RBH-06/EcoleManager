const pool = require('../config/database');

const Teacher = {
  async create(data) {
    const fields = [
      'first_name', 'last_name', 'email', 'phone', 'hire_date', 'status'
    ];
    const values = fields.map(f => data[f] || null);
    const placeholders = fields.map((_, i) => `$${i + 1}`).join(', ');
    const query = `INSERT INTO teachers (${fields.join(', ')}) VALUES (${placeholders}) RETURNING *`;
    const res = await pool.query(query, values);
    return res.rows[0];
  },

  async findAll({ page = 1, limit = 10, search, status, includeInactive = false }) {
    let query = 'SELECT id, first_name, last_name, email, phone, hire_date, status, created_at, updated_at FROM teachers WHERE 1=1';
    const params = [];
    if (search) {
      params.push(`%${search}%`);
      query += ` AND (first_name ILIKE $${params.length} OR last_name ILIKE $${params.length} OR email ILIKE $${params.length})`;
    }
    if (status) {
      params.push(status);
      query += ` AND status = $${params.length}`;
    }
    if (!includeInactive) {
      query += ` AND status != 'inactive'`;
    }
    params.push(limit);
    params.push((page - 1) * limit);
    query += ` ORDER BY created_at DESC LIMIT $${params.length - 1} OFFSET $${params.length}`;
    const res = await pool.query(query, params);
    return res.rows;
  },

  async findById(id) {
    const res = await pool.query('SELECT id, first_name, last_name, email, phone, hire_date, status, created_at, updated_at FROM teachers WHERE id = $1', [id]);
    return res.rows[0];
  },

  async update(id, data) {
    const allowedFields = ['first_name', 'last_name', 'email', 'phone', 'hire_date', 'status'];
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
    const query = `UPDATE teachers SET ${fields.join(', ')}, updated_at = NOW() WHERE id = $${idx} RETURNING *`;
    const res = await pool.query(query, values);
    return res.rows[0];
  },

  // Check if teacher has active classes
  async hasActiveClasses(teacherId) {
    const res = await pool.query(
      `SELECT COUNT(*) as count FROM training_classes 
       WHERE teacher_id = $1 AND status IN ('scheduled', 'ongoing')`,
      [teacherId]
    );
    return parseInt(res.rows[0].count) > 0;
  },

  // Get teacher's active classes
  async getActiveClasses(teacherId) {
    const res = await pool.query(
      `SELECT tc.*, t.name as training_name 
       FROM training_classes tc
       JOIN trainings t ON tc.training_id = t.id
       WHERE tc.teacher_id = $1 AND tc.status IN ('scheduled', 'ongoing')
       ORDER BY tc.start_date`,
      [teacherId]
    );
    return res.rows;
  },

  // Soft delete - mark teacher as inactive
  async softDelete(id) {
    const result = await this.update(id, { status: 'inactive' });
    return result;
  },

  // Hard delete - only if no active classes
  async delete(id) {
    // Check if teacher has active classes
    const hasClasses = await this.hasActiveClasses(id);
    if (hasClasses) {
      throw new Error('Cannot delete teacher with active classes. Use soft delete instead.');
    }
    
    await pool.query('DELETE FROM teachers WHERE id = $1', [id]);
    return true;
  },

  async getSchedule(teacherId, startDate, endDate) {
    const res = await pool.query(
      `SELECT * FROM training_classes WHERE teacher_id = $1 AND start_date >= $2 AND end_date <= $3`,
      [teacherId, startDate, endDate]
    );
    return res.rows;
  }
};

module.exports = Teacher;
