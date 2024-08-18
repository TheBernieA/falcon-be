import prisma from '../prismaClient.mjs';

// Controller function to get all trades
export const getOpenTrades = async (req, res) => {
  try {
    const openTrades = await prisma.trade.findMany();
    res.json(openTrades);
  } catch (error) {
    console.error('Error fetching trades:', error);
    res.status(500).json({ error: 'Internal Server Error' });
  }
};
