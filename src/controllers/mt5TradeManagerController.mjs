import { exec } from 'child_process';
import { promisify } from 'util';
import path from 'path';
import { fileURLToPath } from 'url';

// Get current directory path
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const execPromise = promisify(exec);

// Define the absolute path to the Python script
const pythonScriptPath = path.join(__dirname, '..', 'helpers', 'mt5_trade_manager.py');

// Route to get all open trades
const getAllOpenedTrades = async (req, res) => {
    try {
        const { stdout, stderr } = await execPromise(`python "${pythonScriptPath}" get_open_trades`);

        if (stderr) {
            console.error(`Error: ${stderr}`);
            return res.status(500).json({ error: 'Failed to retrieve open trades' });
        }

        let trades;
        try {
            trades = JSON.parse(stdout);
        } catch (parseError) {
            console.error('Parsing error:', parseError);
            return res.status(500).json({ error: 'Failed to parse open trades data' });
        }

        res.json(trades);
    } catch (error) {
        console.error('Error:', error);
        res.status(500).json({ error: 'Failed to retrieve open trades' });
    }
};

// Route to close all open trades
const closeAllOpenedTrades = async (req, res) => {
    try {
        const { stdout, stderr } = await execPromise(`python "${pythonScriptPath}" close_all_trades`);

        if (stderr) {
            console.error(`Error: ${stderr}`);
            return res.status(500).json({ error: 'Failed to close all trades' });
        }

        let result;
        try {
            result = JSON.parse(stdout);
        } catch (parseError) {
            console.error('Parsing error:', parseError);
            return res.status(500).json({ error: 'Failed to parse close all trades result' });
        }

        res.json(result);
    } catch (error) {
        console.error('Error:', error);
        res.status(500).json({ error: 'Failed to close all trades' });
    }
};

// Route to check if autotrade is active
const checkAutotradeStatus = async (req, res) => {
    try {
        const { stdout, stderr } = await execPromise(`python "${pythonScriptPath}" is_autotrade_active`);

        if (stderr) {
            console.error(`Error: ${stderr}`);
            return res.status(500).json({ error: 'Failed to retrieve autotrade status' });
        }

        let status;
        try {
            status = JSON.parse(stdout);
        } catch (parseError) {
            console.error('Parsing error:', parseError);
            return res.status(500).json({ error: 'Failed to parse autotrade status' });
        }

        res.json(status);
    } catch (error) {
        console.error('Error:', error);
        res.status(500).json({ error: 'Failed to retrieve autotrade status' });
    }
};

// Route to set autotrade status
const setAutotradeStatus = async (req, res) => {
    try {
        const { status } = req.body; // expects { status: boolean }
        if (typeof status !== 'boolean') {
            return res.status(400).json({ error: 'Invalid status value' });
        }

        const statusStr = status ? 'true' : 'false'; // Convert boolean to string
        const { stdout, stderr } = await execPromise(`python "${pythonScriptPath}" set_autotrade ${statusStr}`);

        if (stderr) {
            console.error(`Error: ${stderr}`);
            return res.status(500).json({ error: 'Failed to set autotrade status' });
        }

        let result;
        try {
            result = JSON.parse(stdout);
        } catch (parseError) {
            console.error('Parsing error:', parseError);
            return res.status(500).json({ error: 'Failed to parse set autotrade result' });
        }

        res.json(result);
    } catch (error) {
        console.error('Error:', error);
        res.status(500).json({ error: 'Failed to set autotrade status' });
    }
};

// Route to close all trades in profit
const closeAllTradesInProfit = async (req, res) => {
    try {
        const { stdout, stderr } = await execPromise(`python "${pythonScriptPath}" close_trades_in_profit`);

        if (stderr) {
            console.error(`Error: ${stderr}`);
            return res.status(500).json({ error: 'Failed to close all trades in profit' });
        }

        let result;
        try {
            result = JSON.parse(stdout);
        } catch (parseError) {
            console.error('Parsing error:', parseError);
            return res.status(500).json({ error: 'Failed to parse close trades in profit result' });
        }

        res.json(result);
    } catch (error) {
        console.error('Error:', error);
        res.status(500).json({ error: 'Failed to close all trades in profit' });
    }
};

// Route to close all trades in loss
const closeAllTradesInLoss = async (req, res) => {
    try {
        const { stdout, stderr } = await execPromise(`python "${pythonScriptPath}" close_trades_in_loss`);

        if (stderr) {
            console.error(`Error: ${stderr}`);
            return res.status(500).json({ error: 'Failed to close all trades in loss' });
        }

        let result;
        try {
            result = JSON.parse(stdout);
        } catch (parseError) {
            console.error('Parsing error:', parseError);
            return res.status(500).json({ error: 'Failed to parse close trades in loss result' });
        }

        res.json(result);
    } catch (error) {
        console.error('Error:', error);
        res.status(500).json({ error: 'Failed to close all trades in loss' });
    }
};

export { getAllOpenedTrades, closeAllOpenedTrades, checkAutotradeStatus, setAutotradeStatus, closeAllTradesInProfit, closeAllTradesInLoss };
