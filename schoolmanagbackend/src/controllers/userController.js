const User = require('../models/User');
const AuthService = require('../services/authService');

const UserController = {
  async list(req, res) {
    try {
      const { page, limit, search, role, status } = req.query;
      const users = await User.findAll({ page, limit, search, role, status });
      res.json(users);
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  },

  async get(req, res) {
    try {
      const user = await User.findById(req.params.id);
      if (!user) return res.status(404).json({ error: 'User not found' });
      res.json(user);
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  },

  async update(req, res) {
    try {
      const updated = await User.update(req.params.id, req.body);
      res.json(updated);
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  },

  async remove(req, res) {
    try {
      await User.delete(req.params.id);
      res.json({ success: true });
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  },

  async createSubAdmin(req, res) {
    try {
      const user = await AuthService.register({ ...req.body, role: 'sub_admin' });
      res.status(201).json(user);
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  },

  async assignPermissions(req, res) {
    try {
      // Implement permission assignment logic here
      res.json({ success: true });
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  },

  async dashboardKPIs(req, res) {
    try {
      const pool = require('../config/database');
      const studentsRes = await pool.query('SELECT COUNT(*) FROM students');
      const teachersRes = await pool.query('SELECT COUNT(*) FROM teachers');
      const classesRes = await pool.query('SELECT COUNT(*) FROM training_classes');
      res.json({
        students: parseInt(studentsRes.rows[0].count, 10),
        teachers: parseInt(teachersRes.rows[0].count, 10),
        classes: parseInt(classesRes.rows[0].count, 10)
      });
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  }
};

module.exports = UserController;
