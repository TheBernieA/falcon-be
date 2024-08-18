import cron from 'node-cron';
import { io } from '../server.mjs';
import * as globalState from "../helpers/globalState.mjs";
import prisma from '../prismaClient.mjs';
import { analyzeMarket } from "../models/analyzeMarket.mjs";
import { priceActionStrategy } from '../models/priceActionStrategy.mjs';

let autoTradeTask = null;
let tradeInterval = '*/5 * * * *'; // Default interval: every 5 minutes

// Get bot status
export const getBotStatus = (req, res) => {
    const status = globalState.getAutoTrading() ? 'Active' : 'Inactive';
    res.json({
        status,
        isAnalyzing: globalState.getIsAnalyzing()
    });
};

// Start trade or auto-trade
export const startTrade = async (req, res) => {
    const { userId, symbol, volume, autoTrade, strategy, interval } = req.body;

    if (!userId) {
        return res.status(400).json({ error: 'User ID is required' });
    }

    if (autoTrade) {
        if (globalState.getAutoTrading()) {
            console.log('Auto-trade is already running');
            return res.status(400).json({ message: 'Auto-trade is already running' });
        }

        // Update the trade interval if provided
        if (interval) {
            tradeInterval = `*/${interval} * * * *`; // Cron syntax for every X minutes
        }

        globalState.setAutoTrading(true);
        startAutoTrade(userId, volume, strategy);
        io.emit('bot-status', { status: 'Active', isAnalyzing: globalState.getIsAnalyzing() });
        return res.json({ message: 'Auto-trade started' });
    }

    if (!symbol || typeof symbol !== 'string' || volume <= 0) {
        return res.status(400).json({ error: 'Invalid input parameters' });
    }

    try {
        globalState.setIsAnalyzing(true);
        io.emit('bot-status', { status: globalState.getAutoTrading() ? 'Active' : 'Inactive', isAnalyzing: globalState.getIsAnalyzing() });

        let action;
        if (strategy === 'priceAction') {
            action = await priceActionStrategy(userId, symbol);  // Use priceActionStrategy
        } else {
            const indicators = {
                shortTermMAPeriod: 5,
                longTermMAPeriod: 20,
                rsiPeriod: 14,
                macdShortPeriod: 12,
                macdLongPeriod: 26,
                macdSignalPeriod: 9
            };
            action = await analyzeMarket(userId, symbol, indicators, strategy);
        }

        if (action) {
            // const trade = await placeTrade(userId, symbol, volume, action);
            // io.emit('trade-placed', trade);
            // res.json(trade);
            console.log('Trade opened');

        } else {
            res.status(200).json({ message: 'No action required based on market conditions' });
        }
    } catch (error) {
        console.error('Error in startTrade:', error);
        globalState.setIsAnalyzing(false);
        io.emit('bot-status', { status: globalState.getAutoTrading() ? 'Active' : 'Inactive', isAnalyzing: globalState.getIsAnalyzing() });
        res.status(500).json({ error: 'Internal server error' });
    } finally {
        globalState.setIsAnalyzing(false);
        io.emit('bot-status', { status: globalState.getAutoTrading() ? 'Active' : 'Inactive', isAnalyzing: globalState.getIsAnalyzing() });
    }
};


// Start automatic trading
function startAutoTrade(userId, volume, strategy) {
    if (autoTradeTask) {
        console.log('Auto-trade task is already running');
        return;
    }

    console.log('Starting auto-trade task');
    autoTradeTask = cron.schedule(tradeInterval, async () => {
        try {
            const savedSymbols = await prisma.symbol.findMany({
                where: { userId },
                select: { symbol: true }
            });

            const symbols = savedSymbols.map(record => record.symbol);

            globalState.setIsAnalyzing(true);
            io.emit('bot-status', { status: 'Active', isAnalyzing: globalState.getIsAnalyzing() });

            for (const symbol of symbols) {
                let action;
                if (strategy === 'price_action') {
                    action = await priceActionStrategy(userId, symbol);  // Use priceActionStrategy
                } else {
                    const indicators = {
                        shortTermMAPeriod: 5,
                        longTermMAPeriod: 20,
                        rsiPeriod: 14,
                        macdShortPeriod: 12,
                        macdLongPeriod: 26,
                        macdSignalPeriod: 9
                    };
                    action = await analyzeMarket(userId, symbol, indicators, strategy);
                }

                if (action) {
                    // const trade = await placeTrade(userId, symbol, volume, action);
                    // io.emit('trade-placed', trade);
                    console.log('Trade opened');
                    
                }
            }
        } catch (error) {
            console.error('Error in auto-trade task:', error);
        } finally {
            globalState.setIsAnalyzing(false);
            io.emit('bot-status', { status: 'Active', isAnalyzing: globalState.getIsAnalyzing() });
        }
    });
}


// Stop automatic trading
export const stopTrade = async (req, res) => {
    if (!globalState.getAutoTrading()) {
        console.log('No auto-trade is running');
        return res.status(400).json({ message: 'Auto-trade is not running' });
    }

    console.log('Stopping auto-trade');
    globalState.setAutoTrading(false);
    stopAutoTrade();
    io.emit('bot-status', { status: 'Inactive', isAnalyzing: globalState.getIsAnalyzing() });
    res.json({ message: 'Auto-trade stopped' });
};

// Stop auto-trade task
function stopAutoTrade() {
    if (autoTradeTask) {
        autoTradeTask.stop();
        autoTradeTask = null;
    }
}
