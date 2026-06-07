const express = require('express');
const PaymentController = require('../controllers/paymentController');
const auth = require('../middleware/auth');

const router = express.Router();

router.post('/', auth, PaymentController.recordPayment);
router.get('/student/:studentId', auth, PaymentController.getPaymentHistory);
router.get('/enrollment/:enrollmentId', auth, PaymentController.getPaymentsByEnrollment);
router.get('/outstanding', auth, PaymentController.getOutstandingPayments);

module.exports = router;
