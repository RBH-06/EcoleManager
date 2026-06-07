const jwt = require('jsonwebtoken');
const AuthService = require('../services/authService');

const JWT_SECRET = process.env.JWT_SECRET || 'changeme';

module.exports = async function (req, res, next) {
  try {
    const token = req.header('Authorization')?.replace('Bearer ', '');
    if (!token) return res.status(401).json({ error: 'Access denied' });
    const decoded = jwt.verify(token, JWT_SECRET);
    const user = await AuthService.getUserById(decoded.userId);
    if (!user || !['admin', 'sub_admin'].includes(user.role)) {
      return res.status(403).json({ error: 'Access denied' });
    }
    req.user = user;
    next();
  } catch (error) {
    res.status(401).json({ error: 'Invalid token' });
  }
};
