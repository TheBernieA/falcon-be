import express from 'express';
import dotenv from 'dotenv';
import http from 'http';
import { Server } from 'socket.io';
import cors from 'cors';
import authRoutes from './routes/authRoutes.mjs';
import { router as strategyRoutes } from './routes/executionRoutes.mjs';
import { router as feedbackRoutes } from './routes/feedbackRoutes.mjs';
import { router as symbolsRoutes } from './routes/symbolsRoutes.mjs';
import { router as tradeRoutes } from './routes/tradeRoutes.mjs';
import { router as mt5TradeManagerRoutes } from './routes/mt5TradeManagerRoutes.mjs';
import * as globalState from './helpers/globalState.mjs';

dotenv.config();

const app = express();
const server = http.createServer(app);

const io = new Server(server, {
  cors: {
    origin: 'http://localhost:3000',
    methods: ['GET', 'POST', 'DELETE', 'PUT'], // Add DELETE method here
  },
});


app.use(cors({
  origin: 'http://localhost:3000',
  methods: ['GET', 'POST', 'DELETE', 'PUT'], // Add DELETE method here
  allowedHeaders: ['Content-Type'],
}));


app.use(express.json());

app.use('/auth', authRoutes);
app.use('/', strategyRoutes);
app.use('/', feedbackRoutes);
app.use('/', symbolsRoutes);
app.use('/', tradeRoutes);
app.use('/', mt5TradeManagerRoutes);

io.on('connection', (socket) => {
  console.log('A user connected:', socket.id);

  // Send bot status to the newly connected client
  socket.emit('bot-status', {
    status: globalState.autoTrading ? 'Active' : 'Inactive',
    isAnalyzing: globalState.isAnalyzing,
  });

  socket.on('disconnect', (reason) => {
    console.log(`User disconnected: ${socket.id} Reason: ${reason}`);
  });
});

export { io }

const PORT = process.env.PORT || 8000;
server.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
