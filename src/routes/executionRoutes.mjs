import express from 'express';
import { getBotStatus, startTrade, stopTrade } from '../controllers/executionController.mjs';

export const router = express.Router();


// Start auto-trading
router.post('/trading/start-auto-trade', startTrade);

// Stop auto-trading
router.post('/trading/stop-auto-trade', stopTrade);

// Get bot status
router.get('/trading/bot-status', getBotStatus);