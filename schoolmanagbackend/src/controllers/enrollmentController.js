const Enrollment = require('../models/Enrollment');

const EnrollmentController = {
  async createEnrollment(req, res) {
    try {
      const enrollment = await Enrollment.create(req.body);
      // Return the expanded details after creation
      const detailed = await Enrollment.findByIdWithDetails(enrollment.id);
      res.status(201).json(detailed);
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  },

  async getEnrollments(req, res) {
    try {
      const { page, limit, student_id, class_id, status } = req.query;
      const enrollments = await Enrollment.findAllWithDetails({ page, limit, student_id, class_id, status });
      res.json(enrollments);
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  },

  async getEnrollmentDetails(req, res) {
    try {
      const enrollment = await Enrollment.findByIdWithDetails(req.params.id);
      if (!enrollment) return res.status(404).json({ error: 'Enrollment not found' });
      res.json(enrollment);
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  },

  async updateEnrollment(req, res) {
    try {
      const updated = await Enrollment.update(req.params.id, req.body);
      res.json(updated);
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  },

  async deleteEnrollment(req, res) {
    try {
      await Enrollment.delete(req.params.id);
      res.json({ success: true });
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  }
};

module.exports = EnrollmentController;
