const Teacher = require('../models/Teacher');
const TrainingClass = require('../models/TrainingClass');

const TeacherService = {
  // Reassign all classes from one teacher to another
  async reassignClasses(fromTeacherId, toTeacherId) {
    const client = await Teacher.pool.connect();
    
    try {
      await client.query('BEGIN');
      
      // Get all active classes of the source teacher
      const activeClasses = await Teacher.getActiveClasses(fromTeacherId);
      
      if (activeClasses.length === 0) {
        throw new Error('No active classes found for the source teacher');
      }
      
      // Verify target teacher exists and is active
      const targetTeacher = await Teacher.findById(toTeacherId);
      if (!targetTeacher || targetTeacher.status !== 'active') {
        throw new Error('Target teacher not found or not active');
      }
      
      // Reassign all classes
      const reassignedClasses = [];
      for (const classItem of activeClasses) {
        const updatedClass = await TrainingClass.update(classItem.id, {
          teacher_id: toTeacherId
        });
        reassignedClasses.push(updatedClass);
      }
      
      await client.query('COMMIT');
      
      return {
        success: true,
        message: `Successfully reassigned ${reassignedClasses.length} classes`,
        reassignedClasses,
        fromTeacherId,
        toTeacherId
      };
      
    } catch (error) {
      await client.query('ROLLBACK');
      throw error;
    } finally {
      client.release();
    }
  },

  // Handle teacher departure with class cancellation
  async handleTeacherDeparture(teacherId, options = {}) {
    const { cancelClasses = false, reassignToTeacherId = null } = options;
    
    if (reassignToTeacherId) {
      return await this.reassignClasses(teacherId, reassignToTeacherId);
    }
    
    if (cancelClasses) {
      const client = await Teacher.pool.connect();
      
      try {
        await client.query('BEGIN');
        
        // Get active classes
        const activeClasses = await Teacher.getActiveClasses(teacherId);
        
        // Cancel all classes
        const cancelledClasses = [];
        for (const classItem of activeClasses) {
          const updatedClass = await TrainingClass.update(classItem.id, {
            status: 'cancelled'
          });
          cancelledClasses.push(updatedClass);
        }
        
        // Soft delete the teacher
        const deactivatedTeacher = await Teacher.softDelete(teacherId);
        
        await client.query('COMMIT');
        
        return {
          success: true,
          message: `Teacher deactivated and ${cancelledClasses.length} classes cancelled`,
          cancelledClasses,
          deactivatedTeacher
        };
        
      } catch (error) {
        await client.query('ROLLBACK');
        throw error;
      } finally {
        client.release();
      }
    }
    
    // Just soft delete the teacher
    const deactivatedTeacher = await Teacher.softDelete(teacherId);
    return {
      success: true,
      message: 'Teacher deactivated successfully',
      deactivatedTeacher
    };
  },

  // Get comprehensive teacher information including class dependencies
  async getTeacherWithDependencies(teacherId) {
    const teacher = await Teacher.findById(teacherId);
    if (!teacher) {
      throw new Error('Teacher not found');
    }
    
    const activeClasses = await Teacher.getActiveClasses(teacherId);
    const hasActiveClasses = activeClasses.length > 0;
    
    return {
      teacher,
      hasActiveClasses,
      activeClasses,
      canDelete: !hasActiveClasses,
      canDeactivate: !hasActiveClasses
    };
  }
};

module.exports = TeacherService;
