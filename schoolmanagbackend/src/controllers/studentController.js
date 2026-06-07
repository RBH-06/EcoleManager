const Student = require('../models/Student');

const StudentController = {
  async createStudent(req, res) {
    try {
      const student = await Student.create({ ...req.body, created_by: req.user.id });
      res.status(201).json(student);
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  },

  async getStudents(req, res) {
    try {
      const { page, limit, search, status, sort_by, sort_order } = req.query;
      const students = await Student.findAll({ page, limit, search, status, sort_by, sort_order });
      res.json(students);
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  },

  async getStudentDetails(req, res) {
    try {
      const student = await Student.findByIdWithEnrollments(req.params.id);
      if (!student) return res.status(404).json({ error: 'Student not found' });
      res.json(student);
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  },

  async updateStudent(req, res) {
    try {
      const updated = await Student.update(req.params.id, req.body);
      res.json(updated);
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  },

  async deleteStudent(req, res) {
    try {
      await Student.delete(req.params.id);
      res.json({ success: true });
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  }
};

module.exports = StudentController;
