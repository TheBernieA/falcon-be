import express from 'express';
import { getOpenTrades } from '../controllers/tradesController.mjs';

export const router = express.Router();

// Route to get all open trades
router.get('/trades/open', getOpenTrades);

