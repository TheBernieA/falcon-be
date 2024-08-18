// In your feedback handling controller, e.g., feedbackController.js

import prisma from '../prismaClient.mjs';

export async function feedback(req, res) {
    const { userId, rating, comment, symbol } = req.body;

    // console.log('Received feedback data:', { userId, rating, comment, symbol }); // Log received data

    try {
        const user = await prisma.user.findUnique({
            where: { id: userId },
        });

        if (!user) {
            return res.status(404).json({ message: 'User not found' });
        }

        const feedback = await prisma.feedback.create({
            data: {
                userId,
                rating,
                comment,
                symbol,
            },
        });

        res.status(200).json({ message: 'Feedback submitted successfully', feedback });
    } catch (error) {
        console.error('Error submitting feedback:', error);
        res.status(500).json({ message: 'Error submitting feedback' });
    }
}
