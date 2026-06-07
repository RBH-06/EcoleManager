const express = require('express');
const SessionController = require('../controllers/sessionController');
const auth = require('../middleware/auth');

const router = express.Router();

router.get('/', auth, SessionController.getSessions);
router.post('/', auth, SessionController.createSession);
router.get('/:id', auth, SessionController.getSessionDetails);
router.put('/:id', auth, SessionController.updateSession);
router.delete('/:id', auth, SessionController.deleteSession);

module.exports = router;
