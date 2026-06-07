const SessionPayment = require('../models/SessionPayment');
const Enrollment = require('../models/Enrollment');
const Training = require('../models/Training');
const Session = require('../models/Session');

const sessionPaymentService = {
  // Initialize payment records for all sessions in an enrollment
  async initializeSessionPayments(enrollmentId) {
    try {
      const enrollment = await Enrollment.findById(enrollmentId);
      if (!enrollment) {
        throw new Error('Enrollment not found');
      }

      // Get all sessions for this class
      const sessions = await Session.findByClass(enrollment.class_id);
      
      // Create payment records for each session
      const paymentRecords = [];
      for (const session of sessions) {
        const existingPayment = await SessionPayment.findByEnrollmentAndSession(enrollmentId, session.id);
        if (!existingPayment) {
          const paymentRecord = await SessionPayment.create({
            enrollment_id: enrollmentId,
            session_id: session.id,
            is_paid: false
          });
          paymentRecords.push(paymentRecord);
        }
      }

      return paymentRecords;
    } catch (error) {
      console.error('Error initializing session payments:', error);
      throw error;
    }
  },

  // Calculate payment amount based on training policy
  async calculateSessionPaymentAmount(enrollmentId, sessionId) {
    try {
      const enrollment = await Enrollment.findById(enrollmentId);
      if (!enrollment) {
        throw new Error('Enrollment not found');
      }

      const enrollmentDetails = await Enrollment.findByIdWithDetails(enrollmentId);
      const training = await Training.findById(enrollmentDetails.class.training.id);

      if (enrollment.payment_type === 'per_session') {
        return training.price_per_session;
      } else {
        // For full_training, calculate per session amount
        return training.price_full / training.total_sessions;
      }
    } catch (error) {
      console.error('Error calculating session payment amount:', error);
      throw error;
    }
  },

  // Mark multiple sessions as paid with automatic amount calculation
  async markSessionsAsPaid(enrollmentId, sessionIds, paymentData = {}) {
    try {
      const results = [];
      
      for (const sessionId of sessionIds) {
        // Calculate payment amount if not provided
        if (!paymentData.payment_amount) {
          paymentData.payment_amount = await this.calculateSessionPaymentAmount(enrollmentId, sessionId);
        }

        const result = await SessionPayment.markSessionAsPaid(enrollmentId, sessionId, paymentData);
        results.push(result);
      }

      return results;
    } catch (error) {
      console.error('Error marking sessions as paid:', error);
      throw error;
    }
  },

  // Get comprehensive payment report for a student
  async getStudentPaymentReport(studentId) {
    try {
      const payments = await SessionPayment.findByStudent(studentId);
      
      // Group by enrollment
      const enrollmentGroups = {};
      payments.forEach(payment => {
        if (!enrollmentGroups[payment.enrollment_id]) {
          enrollmentGroups[payment.enrollment_id] = {
            enrollment_id: payment.enrollment_id,
            enrollment_date: payment.enrollment_date,
            class_name: payment.class_name,
            training_name: payment.training_name,
            payment_type: payment.payment_type,
            sessions: []
          };
        }
        enrollmentGroups[payment.enrollment_id].sessions.push(payment);
      });

      // Calculate summary for each enrollment
      const report = Object.values(enrollmentGroups).map(group => {
        const totalSessions = group.sessions.length;
        const paidSessions = group.sessions.filter(s => s.is_paid).length;
        const unpaidSessions = totalSessions - paidSessions;
        const totalPaidAmount = group.sessions
          .filter(s => s.is_paid)
          .reduce((sum, s) => sum + (parseFloat(s.payment_amount) || 0), 0);

        return {
          ...group,
          summary: {
            total_sessions: totalSessions,
            paid_sessions: paidSessions,
            unpaid_sessions: unpaidSessions,
            total_paid_amount: totalPaidAmount
          }
        };
      });

      return report;
    } catch (error) {
      console.error('Error getting student payment report:', error);
      throw error;
    }
  },

  // Get payment status for a specific session across all students
  async getSessionPaymentReport(sessionId) {
    try {
      const payments = await SessionPayment.findBySession(sessionId);
      
      const totalStudents = payments.length;
      const paidStudents = payments.filter(p => p.is_paid).length;
      const unpaidStudents = totalStudents - paidStudents;
      const totalCollected = payments
        .filter(p => p.is_paid)
        .reduce((sum, p) => sum + (parseFloat(p.payment_amount) || 0), 0);

      return {
        session_id: sessionId,
        total_students: totalStudents,
        paid_students: paidStudents,
        unpaid_students: unpaidStudents,
        total_collected: totalCollected,
        student_payments: payments
      };
    } catch (error) {
      console.error('Error getting session payment report:', error);
      throw error;
    }
  },

  // Auto-mark sessions as paid based on training policy
  async autoMarkSessionsAsPaid(enrollmentId, paymentData = {}) {
    try {
      const enrollment = await Enrollment.findById(enrollmentId);
      if (!enrollment) {
        throw new Error('Enrollment not found');
      }

      // If payment type is full_training, mark all sessions as paid
      if (enrollment.payment_type === 'full_training') {
        const payments = await SessionPayment.findByEnrollment(enrollmentId);
        const sessionIds = payments.map(p => p.session_id);
        
        return await this.markSessionsAsPaid(enrollmentId, sessionIds, paymentData);
      }

      return [];
    } catch (error) {
      console.error('Error auto-marking sessions as paid:', error);
      throw error;
    }
  }
};

module.exports = sessionPaymentService; 