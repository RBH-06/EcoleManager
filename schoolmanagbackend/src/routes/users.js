const express = require('express');
const UserController = require('../controllers/userController');
const auth = require('../middleware/auth');

const router = express.Router();

// Dashboard KPIs (must be before any /:id route)
router.get('/dashboard-kpis', auth, UserController.dashboardKPIs);

// Admin only: list all users
router.get('/', auth, UserController.list);
// Admin only: get user by id
router.get('/:id', auth, UserController.get);
// Admin only: update user
router.put('/:id', auth, UserController.update);
// Admin only: delete user
router.delete('/:id', auth, UserController.remove);
// Admin only: create sub-admin
router.post('/', auth, UserController.createSubAdmin);
// Admin only: assign permissions to sub-admin
router.post('/:id/permissions', auth, UserController.assignPermissions);

module.exports = router;
