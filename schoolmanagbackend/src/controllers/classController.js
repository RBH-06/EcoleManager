const TrainingClass = require('../models/TrainingClass');

const ClassController = {
  async createClass(req, res) {
    try {
      const trainingClass = await TrainingClass.create(req.body);
      res.status(201).json(trainingClass);
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  },

  async getClasses(req, res) {
    try {
      const { page, limit, training_id, teacher_id, status } = req.query;
      const classes = await TrainingClass.findAll({ page, limit, training_id, teacher_id, status });
      res.json(classes);
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  },

  async getClassDetails(req, res) {
    try {
      const trainingClass = await TrainingClass.findById(req.params.id);
      if (!trainingClass) return res.status(404).json({ error: 'Class not found' });
      res.json(trainingClass);
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  },

  async updateClass(req, res) {
    try {
      const updated = await TrainingClass.update(req.params.id, req.body);
      res.json(updated);
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  },

  async deleteClass(req, res) {
    try {
      await TrainingClass.delete(req.params.id);
      res.json({ success: true });
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  }
};

module.exports = ClassController;
