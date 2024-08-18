import express from 'express';
import { deleteSymbol, getSymbols, saveSymbol } from '../controllers/symbolsController.mjs';

export const router = express.Router();

router.get('/symbols', getSymbols)
router.post('/symbols', saveSymbol)
router.delete('/symbols', deleteSymbol);