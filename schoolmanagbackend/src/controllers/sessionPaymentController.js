const SessionPayment = require('../models/SessionPayment');
const Enrollment = require('../models/Enrollment');
const Training = require('../models/Training');

const sessionPaymentController = {
  // Get payment status for all sessions of a student
  async getStudentSessionPayments(req, res) {
    try {
      const { studentId } = req.params;
      const payments = await SessionPayment.findByStudent(studentId);
      
      res.json({
        success: true,
        data: payments
      });
    } catch (error) {
      console.error('Error getting student session payments:', error);
      res.status(500).json({
        success: false,
        message: 'Failed to get student session payments',
        error: error.message
      });
    }
  },

  // Get payment status for all sessions of an enrollment
  async getEnrollmentSessionPayments(req, res) {
    try {
      const { enrollmentId } = req.params;
      const payments = await SessionPayment.findByEnrollment(enrollmentId);
      const summary = await SessionPayment.getPaymentSummary(enrollmentId);
      
      res.json({
        success: true,
        data: {
          payments,
          summary
        }
      });
    } catch (error) {
      console.error('Error getting enrollment session payments:', error);
      res.status(500).json({
        success: false,
        message: 'Failed to get enrollment session payments',
        error: error.message
      });
    }
  },

  // Get payment status for all students in a session
  async getSessionPaymentStatus(req, res) {
    try {
      const { sessionId } = req.params;
      const payments = await SessionPayment.findBySession(sessionId);
      
      res.json({
        success: true,
        data: payments
      });
    } catch (error) {
      console.error('Error getting session payment status:', error);
      res.status(500).json({
        success: false,
        message: 'Failed to get session payment status',
        error: error.message
      });
    }
  },

  // Mark a session as paid for a specific enrollment
  async markSessionAsPaid(req, res) {
    try {
      const { enrollmentId, sessionId } = req.params;
      const { payment_date, payment_amount, payment_method, transaction_reference, notes } = req.body;

      // Validate enrollment exists
      const enrollment = await Enrollment.findById(enrollmentId);
      if (!enrollment) {
        return res.status(404).json({
          success: false,
          message: 'Enrollment not found'
        });
      }

      // Get training info to determine payment amount if not provided
      let finalPaymentAmount = payment_amount;
      if (!finalPaymentAmount) {
        const enrollmentDetails = await Enrollment.findByIdWithDetails(enrollmentId);
        const training = await Training.findById(enrollmentDetails.class.training.id);
        
        if (enrollment.payment_type === 'per_session') {
          finalPaymentAmount = training.price_per_session;
        } else {
          // For full_training, we might want to calculate per session amount
          finalPaymentAmount = training.price_full / training.total_sessions;
        }
      }

      const paymentData = {
        payment_date: payment_date || new Date().toISOString().split('T')[0],
        payment_amount: finalPaymentAmount,
        payment_method,
        transaction_reference,
        notes,
        marked_by: req.user.id
      };

      const result = await SessionPayment.markSessionAsPaid(enrollmentId, sessionId, paymentData);
      
      res.json({
        success: true,
        message: 'Session marked as paid successfully',
        data: result
      });
    } catch (error) {
      console.error('Error marking session as paid:', error);
      res.status(500).json({
        success: false,
        message: 'Failed to mark session as paid',
        error: error.message
      });
    }
  },

  // Mark a session as unpaid for a specific enrollment
  async markSessionAsUnpaid(req, res) {
    try {
      const { enrollmentId, sessionId } = req.params;

      const result = await SessionPayment.markSessionAsUnpaid(enrollmentId, sessionId);
      
      res.json({
        success: true,
        message: 'Session marked as unpaid successfully',
        data: result
      });
    } catch (error) {
      console.error('Error marking session as unpaid:', error);
      res.status(500).json({
        success: false,
        message: 'Failed to mark session as unpaid',
        error: error.message
      });
    }
  },

  // Bulk mark multiple sessions as paid
  async bulkMarkSessionsAsPaid(req, res) {
    try {
      const { enrollmentId } = req.params;
      const { sessionIds, payment_data } = req.body;

      if (!Array.isArray(sessionIds) || sessionIds.length === 0) {
        return res.status(400).json({
          success: false,
          message: 'sessionIds array is required'
        });
      }

      const results = [];
      for (const sessionId of sessionIds) {
        const result = await SessionPayment.markSessionAsPaid(enrollmentId, sessionId, payment_data);
        results.push(result);
      }

      res.json({
        success: true,
        message: `${results.length} sessions marked as paid successfully`,
        data: results
      });
    } catch (error) {
      console.error('Error bulk marking sessions as paid:', error);
      res.status(500).json({
        success: false,
        message: 'Failed to bulk mark sessions as paid',
        error: error.message
      });
    }
  },

  // Get payment summary for an enrollment
  async getPaymentSummary(req, res) {
    try {
      const { enrollmentId } = req.params;
      const summary = await SessionPayment.getPaymentSummary(enrollmentId);
      
      res.json({
        success: true,
        data: summary
      });
    } catch (error) {
      console.error('Error getting payment summary:', error);
      res.status(500).json({
        success: false,
        message: 'Failed to get payment summary',
        error: error.message
      });
    }
  }
};

module.exports = sessionPaymentController; 