// // helpers/tradeUtils.js
// import { execFile } from 'child_process';
// import path from 'path';
// import prisma from '../prismaClient.mjs';
// import { fileURLToPath } from 'url';


// const __filename = fileURLToPath(import.meta.url);
// const __dirname = path.dirname(__filename);

// export async function placeTrade(userId, symbol, volume, action, scriptName) {
//     if (!userId || !symbol || volume <= 0 || !action) {
//         throw new Error('Invalid trade parameters');
//     }

//     try {
//         // const trade = await prisma.trade.create({
//         //     data: { userId, symbol, volume, action },
//         // });
//         // console.log('Trade placed:', trade);

//         // Call Python script to place trade on MT5
//         const scriptPath = path.join(__dirname, `${scriptName}`);
//         const args = [symbol, volume.toString(), action];
//         execFile('python', [scriptPath, ...args], (error, stdout, stderr) => {
//             if (error) {
//                 console.error('Error executing Python script:', error);
//                 return;
//             }
//             if (stderr) {
//                 console.error('Python script stderr:', stderr);
//                 return;
//             }
//             console.log('Python script output:', stdout);
//         });

//         // return trade;
//     } catch (error) {
//         console.error('Error placing trade:', error);
//         throw error;
//     }
// }
