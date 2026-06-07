const Session = require('../models/Session');

const SessionController = {
  async createSession(req, res) {
    try {
      const session = await Session.create(req.body);
      res.status(201).json(session);
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  },

  async getSessions(req, res) {
    try {
      const { page, limit, class_id, status } = req.query;
      const sessions = await Session.findAll({ page, limit, class_id, status });
      res.json(sessions);
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  },

  async getSessionDetails(req, res) {
    try {
      const session = await Session.findById(req.params.id);
      if (!session) return res.status(404).json({ error: 'Session not found' });
      res.json(session);
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  },

  async updateSession(req, res) {
    try {
      const updated = await Session.update(req.params.id, req.body);
      res.json(updated);
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  },

  async deleteSession(req, res) {
    try {
      await Session.delete(req.params.id);
      res.json({ success: true });
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  }
};

module.exports = SessionController;
