const express = require('express');
const StudentController = require('../controllers/studentController');
const auth = require('../middleware/auth');

const router = express.Router();

router.get('/', auth, StudentController.getStudents);
router.post('/', auth, StudentController.createStudent);
router.get('/:id', auth, StudentController.getStudentDetails);
router.put('/:id', auth, StudentController.updateStudent);
router.delete('/:id', auth, StudentController.deleteStudent);

module.exports = router;
