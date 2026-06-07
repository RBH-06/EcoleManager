const express = require('express');
const TrainingController = require('../controllers/trainingController');
const auth = require('../middleware/auth');

const router = express.Router();

router.get('/', auth, TrainingController.getTrainings);
router.post('/', auth, TrainingController.createTraining);
router.get('/:id', auth, TrainingController.getTrainingDetails);
router.put('/:id', auth, TrainingController.updateTraining);
router.delete('/:id', auth, TrainingController.deleteTraining);

module.exports = router;
