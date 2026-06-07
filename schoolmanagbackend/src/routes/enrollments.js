const express = require('express');
const EnrollmentController = require('../controllers/enrollmentController');
const auth = require('../middleware/auth');

const router = express.Router();

router.get('/', auth, EnrollmentController.getEnrollments);
router.post('/', auth, EnrollmentController.createEnrollment);
router.get('/:id', auth, EnrollmentController.getEnrollmentDetails);
router.put('/:id', auth, EnrollmentController.updateEnrollment);
router.delete('/:id', auth, EnrollmentController.deleteEnrollment);

module.exports = router;
