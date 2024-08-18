import prisma from '../prismaClient.mjs';
import { mt5Login } from '../services/mt5Service.mjs';

export async function login(req, res) {
  const { login, password, server } = req.body;

  if (!login || !password || !server) {
    return res.status(400).json({ error: 'Missing login, password, or server' });
  }

  try {
    const loginResult = await mt5Login(login, password, server);

    if (loginResult.success) {
      let user = await prisma.user.findUnique({ where: { login } });
      if (!user) {
        user = await prisma.user.create({
          data: {
            login,
            password,
            server,
          },
        });
      }
      res.json({ success: true, user });
    } else {
      res.status(401).json({ error: 'Login failed' });
    }
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'Internal server error' });
  }
}

