const express = require('express');
const TeacherController = require('../controllers/teacherController');
const auth = require('../middleware/auth');

const router = express.Router();

router.get('/', auth, TeacherController.getTeachers);
router.post('/', auth, TeacherController.createTeacher);
router.get('/:id', auth, TeacherController.getTeacherDetails);
router.put('/:id', auth, TeacherController.updateTeacher);
router.delete('/:id', auth, TeacherController.deleteTeacher);
router.get('/:id/schedule', auth, TeacherController.getTeacherSchedule);

// New routes for better deletion handling
router.get('/:id/check-deletion', auth, TeacherController.checkTeacherDeletion);
router.post('/:id/soft-delete', auth, TeacherController.softDeleteTeacher);
router.get('/:id/active-classes', auth, TeacherController.getTeacherActiveClasses);

// Advanced teacher management routes
router.get('/:id/with-dependencies', auth, TeacherController.getTeacherWithDependencies);
router.post('/reassign-classes', auth, TeacherController.reassignClasses);
router.post('/:id/handle-departure', auth, TeacherController.handleTeacherDeparture);

module.exports = router;
