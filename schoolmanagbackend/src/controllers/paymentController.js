const Payment = require('../models/Payment');

const PaymentController = {
  async recordPayment(req, res) {
    try {
      const payment = await Payment.create({ ...req.body, created_by: req.user.id, status: 'completed' });
      res.status(201).json(payment);
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  },

  async getPaymentHistory(req, res) {
    try {
      const { studentId, startDate, endDate } = req.query;
      const payments = await Payment.getStudentPayments(studentId, startDate, endDate);
      res.json(payments);
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  },

  async getPaymentsByEnrollment(req, res) {
    try {
      const { enrollmentId } = req.params;
      const payments = await Payment.findAll({ enrollment_id: enrollmentId });
      res.json(payments);
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  },

  async getOutstandingPayments(req, res) {
    try {
      const payments = await Payment.getOutstandingPayments();
      res.json(payments);
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  }
};

module.exports = PaymentController;
