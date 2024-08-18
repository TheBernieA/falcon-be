import axios from 'axios';
import prisma from '../prismaClient.mjs';

// export const openAiApiKey = process.env.OPENAI_API_KEY;  // Use environment variable for API key

export async function processFeedback(feedback) {
    try {
        const prompt = `Analyze the following feedback to provide insights that can be used to adjust the trading strategy:\n\nFeedback: ${feedback.comment}\nRating: ${feedback.rating}\n\nProvide any recommendations or adjustments for the trading strategy.`;

        const response = await axios.post('https://api.openai.com/v1/chat/completions', {
            model: 'gpt-3.5-turbo',
            messages: [
                { role: 'system', content: 'You are a helpful assistant.' },
                { role: 'user', content: prompt }
            ],
            max_tokens: 150,
            temperature: 0.7,
        }, {
            headers: {
                'Authorization': `Bearer ${openAiApiKey}`,
                'Content-Type': 'application/json',
            },
        });

        const insights = response.data.choices[0].message.content.trim();
        console.log('OpenAI insights:', insights);

        await updateStrategyParameters(feedback.userId, insights);

    } catch (error) {
        handleApiError(error);
    }
}

export async function updateStrategyParameters(userId, insights) {
    try {
        const parameters = parseInsights(insights);

        if (!parameters) {
            console.error('No valid parameters found in insights');
            return;
        }

        await prisma.strategySettings.upsert({
            where: { userId },
            update: parameters,
            create: {
                userId,
                ...parameters
            }
        });

        console.log('Strategy parameters updated successfully');
    } catch (error) {
        console.error('Error updating strategy parameters:', error);
    }
}

function parseInsights(insights) {
    try {
        const parsedInsights = JSON.parse(insights);
        return {
            shortTermMAPeriod: parsedInsights.shortTermMAPeriod,
            longTermMAPeriod: parsedInsights.longTermMAPeriod,
            rsiPeriod: parsedInsights.rsiPeriod,
            macdShortPeriod: parsedInsights.macdShortPeriod,
            macdLongPeriod: parsedInsights.macdLongPeriod,
            macdSignalPeriod: parsedInsights.macdSignalPeriod
        };
    } catch (error) {
        console.error('Error parsing insights:', error);
        return null;
    }
}

function handleApiError(error) {
    if (error.response) {
        console.error('Error response data:', error.response.data);
        console.error('Error response status:', error.response.status);
        console.error('Error response headers:', error.response.headers);
    } else if (error.request) {
        console.error('Error request data:', error.request);
    } else {
        console.error('Error message:', error.message);
    }
}
