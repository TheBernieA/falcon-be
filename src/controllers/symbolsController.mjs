import prisma from '../prismaClient.mjs';

// Fetch symbols for a user
export const getSymbols = async (req, res) => {
    const { userId } = req.query; // Extract userId from query parameters

    if (!userId) {
        return res.status(400).json({ error: 'User ID is required' });
    }

    try {
        // Fetch symbols associated with the userId from the database
        const symbols = await prisma.symbol.findMany({
            where: { userId }
        });

        res.json(symbols);
    } catch (error) {
        console.error('Error fetching symbols:', error);
        res.status(500).json({ error: 'Failed to fetch symbols' });
    }
};

// Save symbols for a user
export const saveSymbol = async (req, res) => {
    const { symbols, userId } = req.body;
    if (!Array.isArray(symbols)) {
        return res.status(400).json({ error: 'Symbols must be an array' });
    }

    try {
        // Remove existing symbols for the user
        await prisma.symbol.deleteMany({ where: { userId } });

        // Save new symbols
        const savedSymbols = await Promise.all(symbols.map(symbol =>
            prisma.symbol.create({ data: { userId, symbol } })
        ));

        res.json(savedSymbols);
    } catch (error) {
        console.error('Error saving symbols:', error);
        res.status(500).json({ error: 'Failed to save symbols' });
    }
};

// Delete a specific symbol
export const deleteSymbol = async (req, res) => {
    const { userId, symbol } = req.body;

    if (!userId || !symbol) {
        return res.status(400).json({ error: 'User ID and symbol are required' });
    }

    try {
        await prisma.symbol.deleteMany({
            where: {
                userId: userId,
                symbol: symbol, // Ensure this is a string
            },
        });
        res.status(200).json({ message: 'Symbol deleted successfully' });
    } catch (error) {
        console.error('Error deleting symbol:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
};