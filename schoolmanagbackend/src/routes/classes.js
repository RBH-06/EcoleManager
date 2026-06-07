const express = require('express');
const ClassController = require('../controllers/classController');
const auth = require('../middleware/auth');

const router = express.Router();

router.get('/', auth, ClassController.getClasses);
router.post('/', auth, ClassController.createClass);
router.get('/:id', auth, ClassController.getClassDetails);
router.put('/:id', auth, ClassController.updateClass);
router.delete('/:id', auth, ClassController.deleteClass);

module.exports = router;
