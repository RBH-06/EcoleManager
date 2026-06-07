const express = require('express');
const router = express.Router();
const sessionPaymentController = require('../controllers/sessionPaymentController');
const { authenticateToken } = require('../middleware/auth');
const { checkPermission } = require('../middleware/permissions');

// Apply authentication to all routes
router.use(authenticateToken);

// Get payment status for all sessions of a student
router.get('/student/:studentId', 
  checkPermission('view_payments'), 
  sessionPaymentController.getStudentSessionPayments
);

// Get payment status for all sessions of an enrollment
router.get('/enrollment/:enrollmentId', 
  checkPermission('view_payments'), 
  sessionPaymentController.getEnrollmentSessionPayments
);

// Get payment status for all students in a session
router.get('/session/:sessionId', 
  checkPermission('view_payments'), 
  sessionPaymentController.getSessionPaymentStatus
);

// Mark a session as paid for a specific enrollment
router.post('/enrollment/:enrollmentId/session/:sessionId/mark-paid', 
  checkPermission('view_payments'), 
  sessionPaymentController.markSessionAsPaid
);

// Mark a session as unpaid for a specific enrollment
router.post('/enrollment/:enrollmentId/session/:sessionId/mark-unpaid', 
  checkPermission('view_payments'), 
  sessionPaymentController.markSessionAsUnpaid
);

// Bulk mark multiple sessions as paid
router.post('/enrollment/:enrollmentId/bulk-mark-paid', 
  checkPermission('view_payments'), 
  sessionPaymentController.bulkMarkSessionsAsPaid
);

// Get payment summary for an enrollment
router.get('/enrollment/:enrollmentId/summary', 
  checkPermission('view_payments'), 
  sessionPaymentController.getPaymentSummary
);

module.exports = router; 