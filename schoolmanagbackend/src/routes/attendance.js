const express = require('express');
const AttendanceController = require('../controllers/attendanceController');
const auth = require('../middleware/auth');

const router = express.Router();

// Get attendance for a session
router.get('/sessions/:session_id/attendance', auth, AttendanceController.getSessionAttendance);
// Bulk update attendance for a session
router.put('/sessions/:session_id/attendance', auth, AttendanceController.bulkUpdateSessionAttendance);
// Update a single student's attendance for a session
router.put('/sessions/:session_id/students/:student_id/attendance', auth, AttendanceController.updateStudentAttendance);
// Delete a student's attendance for a session
router.delete('/sessions/:session_id/students/:student_id/attendance', auth, AttendanceController.deleteStudentAttendance);

module.exports = router;
