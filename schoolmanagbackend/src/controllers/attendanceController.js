const Attendance = require('../models/Attendance');

const AttendanceController = {
  // Get all attendance for a session (all students in the class, with their attendance status)
  async getSessionAttendance(req, res) {
    try {
      const { session_id } = req.params;
      const attendance = await Attendance.getSessionAttendanceWithStudents(session_id);
      res.json(attendance);
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  },

  // Bulk update attendance for a session
  async bulkUpdateSessionAttendance(req, res) {
    try {
      const { session_id } = req.params;
      const { attendance } = req.body;
      if (!Array.isArray(attendance)) {
        return res.status(400).json({ error: 'attendance must be an array' });
      }
      const result = await Attendance.bulkUpsert(session_id, attendance);
      res.json(result);
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  },

  // Update a single student's attendance for a session
  async updateStudentAttendance(req, res) {
    try {
      const { session_id, student_id } = req.params;
      const { status, notes } = req.body;
      const result = await Attendance.upsert(session_id, student_id, status, notes);
      res.json(result);
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  },

  // Delete a student's attendance for a session
  async deleteStudentAttendance(req, res) {
    try {
      const { session_id, student_id } = req.params;
      await Attendance.delete(session_id, student_id);
      res.json({ success: true });
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  }
};

module.exports = AttendanceController;
