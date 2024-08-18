import { execFile } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';
import prisma from '../prismaClient.mjs';
import { io } from '../server.mjs';
import * as globalState from '../helpers/globalState.mjs'; // Import entire module
import { processFeedback } from '../helpers/strategyHelper.mjs';

// Resolve the current directory
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Function to place a trade
export async function placeTrade(userId, symbol, volume, action) {
    if (!userId || !symbol || volume <= 0 || !action) {
        throw new Error('Invalid trade parameters');
    }

    try {
        // Call Python script to place trade on MT5
        const scriptPath = path.join(__dirname, '../helpers/swing_trading.py');
        const args = [symbol, volume.toString(), action];
        execFile('python', [scriptPath, ...args], (error, stdout, stderr) => {
            if (error) {
                console.error('Error executing Python script:', error);
                return;
            }
            if (stderr) {
                console.error('Python script stderr:', stderr);
                return;
            }
            console.log('Python script output:', stdout);
        });

    } catch (error) {
        console.error('Error placing trade:', error);
        throw error;
    }
}

// Analyze market and decide on trades
export async function analyzeSwingStrategy(userId, symbol, indicators) {
    try {
        console.log(`Analyzing market for symbol: ${symbol}, type of symbol: ${typeof symbol}`);

        if (typeof symbol !== 'string') {
            throw new Error('Symbol must be a string');
        }

        // Call Python script for market analysis
        const scriptPath = path.join(__dirname, '../helpers/swing_trading.py');
        const args = [symbol, '1', 'buy', ...Object.values(indicators)];
        execFile('python', [scriptPath, ...args], (error, stdout, stderr) => {
            if (error) {
                console.error('Error executing Python script:', error);
                return;
            }
            if (stderr) {
                console.error('Python script stderr:', stderr);
                return;
            }
            console.log('Python script output:', stdout);
            // Based on the output, decide if you need to place a trade
        });

    } catch (error) {
        console.error(`Error analyzing market for ${symbol}:`, error);
    }
}

// Function to process feedback and update strategy
export async function handleFeedback(feedback) {
    try {
        await processFeedback(feedback);
        const userId = feedback.userId;
        const strategyParameters = await prisma.strategySettings.findUnique({ where: { userId } });

        if (strategyParameters) {
            const symbol = feedback.symbol; // Ensure the feedback contains the symbol
            await analyzeSwingStrategy(userId, symbol, strategyParameters);
        }
    } catch (error) {
        console.error('Error handling feedback:', error);
    }
}
