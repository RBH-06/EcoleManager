const Training = require('../models/Training');

const TrainingController = {
  async createTraining(req, res) {
    try {
      const training = await Training.create({ ...req.body, created_by: req.user.id });
      res.status(201).json(training);
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  },

  async getTrainings(req, res) {
    try {
      const { page, limit, status } = req.query;
      const trainings = await Training.findAll({ page, limit, status });
      res.json(trainings);
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  },

  async getTrainingDetails(req, res) {
    try {
      const training = await Training.findById(req.params.id);
      if (!training) return res.status(404).json({ error: 'Training not found' });
      res.json(training);
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  },

  async updateTraining(req, res) {
    try {
      const updated = await Training.update(req.params.id, req.body);
      res.json(updated);
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  },

  async deleteTraining(req, res) {
    try {
      await Training.delete(req.params.id);
      res.json({ success: true });
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  }
};

module.exports = TrainingController;
