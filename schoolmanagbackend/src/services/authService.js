const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const pool = require('../config/database');

const JWT_SECRET = process.env.JWT_SECRET || 'changeme';
const JWT_EXPIRES_IN = '7d';

const AuthService = {
  async register({ email, password, first_name, last_name, phone, role }) {
    const userCheck = await pool.query('SELECT * FROM users WHERE email = $1', [email]);
    if (userCheck.rows.length > 0) throw new Error('User already exists');
    const password_hash = await bcrypt.hash(password, 10);
    const result = await pool.query(
      `INSERT INTO users (email, password_hash, first_name, last_name, phone, role) 
       VALUES ($1, $2, $3, $4, $5, $6) RETURNING *`,
      [email, password_hash, first_name, last_name, phone, role || 'sub_admin']
    );
    return result.rows[0];
  },

  async login({ email, password }) {
    const userRes = await pool.query('SELECT * FROM users WHERE email = $1', [email]);
    const user = userRes.rows[0];
    if (!user) throw new Error('Invalid credentials');
    const valid = await bcrypt.compare(password, user.password_hash);
    if (!valid) throw new Error('Invalid credentials');
    if (!['admin', 'sub_admin'].includes(user.role)) throw new Error('Access denied');
    const token = jwt.sign({ userId: user.id, role: user.role }, JWT_SECRET, { expiresIn: JWT_EXPIRES_IN });
    return { token, user };
  },

  async getUserById(id) {
    const res = await pool.query('SELECT * FROM users WHERE id = $1', [id]);
    return res.rows[0];
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

module.exports = AuthService;
