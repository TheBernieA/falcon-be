import { execFile } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export const priceActionStrategy = async (userId, symbol) => {
    console.log('Price action strategy', symbol);

    const SYMBOL = symbol;
    const LOT_SIZE = 0.1;  // Lot size for each trade
    const STOP_LOSS_PIPS = 10;  // Stop loss in pips
    const TAKE_PROFIT_PIPS = 20;  // Take profit in pips

    // Function to analyze market and decide action by calling the Python script
    const analyzeMarketAndDecideAction = () => {
        return new Promise((resolve, reject) => {
            const scriptPath = path.join(__dirname, '../helpers/price_action_script.py'); // Ensure this path is correct
            const args = [SYMBOL, LOT_SIZE.toString(), STOP_LOSS_PIPS.toString(), TAKE_PROFIT_PIPS.toString()];

            execFile('python', [scriptPath, ...args], (error, stdout, stderr) => {
                if (error) {
                    console.error(`Error executing script: ${error.message}`);
                    return reject(error);
                }
                if (stderr) {
                    console.error(`Python stderr: ${stderr}`);
                    return reject(new Error(stderr));
                }

                const action = stdout.trim();
                console.log(`Market analysis result: ${action}`);
                resolve(action);
            });
        });
    };

    // Function to place a trade
    const placeTrade = async (symbol, volume, action) => {
        if (!symbol || volume <= 0 || !action) {
            throw new Error('Invalid trade parameters');
        }

        try {
            const scriptPath = path.join(__dirname, '../helpers/price_action_trade.py'); // Ensure this path is correct
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
    };

    try {
        const action = await analyzeMarketAndDecideAction();
        if (action && (action === 'buy' || action === 'sell')) {
            await placeTrade(SYMBOL, LOT_SIZE, action);
        }
        return action;
    } catch (error) {
        console.error(`Error in price action strategy: ${error.message}`);
        return null;
    }
};
