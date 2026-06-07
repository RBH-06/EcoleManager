const Teacher = require('../models/Teacher');
const TeacherService = require('../services/teacherService');

const TeacherController = {
  async createTeacher(req, res) {
    try {
      const teacher = await Teacher.create({ ...req.body, created_by: req.user.id });
      res.status(201).json(teacher);
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  },

  async getTeachers(req, res) {
    try {
      const { page, limit, search, status, includeInactive } = req.query;
      const teachers = await Teacher.findAll({ page, limit, search, status, includeInactive });
      res.json(teachers);
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  },

  async getTeacherDetails(req, res) {
    try {
      const teacher = await Teacher.findById(req.params.id);
      if (!teacher) return res.status(404).json({ error: 'Teacher not found' });
      res.json(teacher);
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  },

  async updateTeacher(req, res) {
    try {
      const updated = await Teacher.update(req.params.id, req.body);
      res.json(updated);
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  },

  // Check if teacher can be deleted
  async checkTeacherDeletion(req, res) {
    try {
      const teacherId = req.params.id;
      const hasActiveClasses = await Teacher.hasActiveClasses(teacherId);
      const activeClasses = hasActiveClasses ? await Teacher.getActiveClasses(teacherId) : [];
      
      res.json({
        canDelete: !hasActiveClasses,
        hasActiveClasses,
        activeClasses,
        message: hasActiveClasses 
          ? 'Teacher has active classes. Use soft delete instead.' 
          : 'Teacher can be safely deleted.'
      });
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  },

  // Soft delete - mark teacher as inactive
  async softDeleteTeacher(req, res) {
    try {
      const teacherId = req.params.id;
      const hasActiveClasses = await Teacher.hasActiveClasses(teacherId);
      
      if (hasActiveClasses) {
        const activeClasses = await Teacher.getActiveClasses(teacherId);
        return res.status(400).json({
          error: 'Cannot deactivate teacher with active classes',
          activeClasses,
          suggestion: 'Please reassign or cancel active classes first'
        });
      }

      const result = await Teacher.softDelete(teacherId);
      res.json({
        success: true,
        message: 'Teacher deactivated successfully',
        teacher: result
      });
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  },

  // Hard delete - only if no active classes
  async deleteTeacher(req, res) {
    try {
      const teacherId = req.params.id;
      const hasActiveClasses = await Teacher.hasActiveClasses(teacherId);
      
      if (hasActiveClasses) {
        const activeClasses = await Teacher.getActiveClasses(teacherId);
        return res.status(400).json({
          error: 'Cannot delete teacher with active classes',
          activeClasses,
          suggestion: 'Use soft delete instead or reassign classes first'
        });
      }

      await Teacher.delete(teacherId);
      res.json({ 
        success: true,
        message: 'Teacher deleted successfully'
      });
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  },

  async getTeacherSchedule(req, res) {
    try {
      const { startDate, endDate } = req.query;
      const schedule = await Teacher.getSchedule(req.params.id, startDate, endDate);
      res.json(schedule);
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  },

  // Get teacher's active classes
  async getTeacherActiveClasses(req, res) {
    try {
      const teacherId = req.params.id;
      const activeClasses = await Teacher.getActiveClasses(teacherId);
      res.json(activeClasses);
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  },

  // Get comprehensive teacher information with dependencies
  async getTeacherWithDependencies(req, res) {
    try {
      const teacherId = req.params.id;
      const result = await TeacherService.getTeacherWithDependencies(teacherId);
      res.json(result);
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  },

  // Reassign classes from one teacher to another
  async reassignClasses(req, res) {
    try {
      const { fromTeacherId, toTeacherId } = req.body;
      
      if (!fromTeacherId || !toTeacherId) {
        return res.status(400).json({ 
          error: 'Both fromTeacherId and toTeacherId are required' 
        });
      }

      const result = await TeacherService.reassignClasses(fromTeacherId, toTeacherId);
      res.json(result);
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  },

  // Handle teacher departure with options
  async handleTeacherDeparture(req, res) {
    try {
      const teacherId = req.params.id;
      const { cancelClasses, reassignToTeacherId } = req.body;
      
      const result = await TeacherService.handleTeacherDeparture(teacherId, {
        cancelClasses,
        reassignToTeacherId
      });
      
      res.json(result);
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  }
};

module.exports = TeacherController;
