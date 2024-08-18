// routes.mjs
import express from 'express';
import { closeAllOpenedTrades, getAllOpenedTrades, checkAutotradeStatus, setAutotradeStatus, closeAllTradesInProfit, closeAllTradesInLoss } from '../controllers/mt5TradeManagerController.mjs';

export const router = express.Router();

// Route to get all open trades
router.get('/api/open_trades', getAllOpenedTrades);

// Route to close all open trades
router.post('/api/close_trades', closeAllOpenedTrades);

// Route to check autotrade status
router.get('/api/get_auto_trade_status', checkAutotradeStatus);

// Route to set autotrade status
router.post('/api/set_auto_trade_status', setAutotradeStatus);

// Route to close all trades in profit
router.post('/api/close_trades_in_profit', closeAllTradesInProfit);

// Route to close all trades in loss
router.post('/api/close_trades_in_loss', closeAllTradesInLoss);