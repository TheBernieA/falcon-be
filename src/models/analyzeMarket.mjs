import { analyzeScalpingStrategy } from "./scalpingStrategy.mjs";
import { analyzeSwingStrategy } from "./swingStrategy.mjs";
import { analyzeMomentumStrategy } from "./momentumStrategy.mjs";
import { priceActionStrategy } from "./priceActionStrategy.mjs";

export const analyzeMarket = async (userId, symbol, indicators, strategy) => {
    // Implement your strategy logic based on the strategy parameter
    switch (strategy) {
        case 'swing':
            return analyzeSwingStrategy(userId, symbol, indicators);
        case 'momentum':
            return analyzeMomentumStrategy(userId, symbol, indicators);
        case 'scalping':
            return analyzeScalpingStrategy(userId, symbol, indicators);
        case 'price_action':
            return priceActionStrategy(userId, symbol);
        default:
            throw new Error('Unknown strategy');
    }
};
