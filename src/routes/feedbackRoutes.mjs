import express from 'express';
import { feedback } from '../controllers/feedbackController.mjs';

export const router = express.Router();

router.post('/feedback', feedback);