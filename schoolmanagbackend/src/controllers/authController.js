const AuthService = require('../services/authService');

const AuthController = {
  async register(req, res) {
    try {
      const user = await AuthService.register(req.body);
      res.status(201).json(user);
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  },

  async login(req, res) {
    try {
      const { token, user } = await AuthService.login(req.body);
      res.json({ token, user });
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  },

  async me(req, res) {
    try {
      res.json(req.user);
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  }
};

module.exports = AuthController;
