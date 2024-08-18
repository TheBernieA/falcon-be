import { execFile } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';

// Resolve the current directory
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export async function mt5Login(login, password, server) {
  
  return new Promise((resolve, reject) => {
    // Adjust the script path based on your directory structure
    const scriptPath = path.resolve(__dirname, 'mt5_login.py');
    
    const process = execFile('python', [scriptPath, login, password, server], (error, stdout, stderr) => {
      if (error) {
        console.error('Error executing Python script:', stderr);
        reject(new Error('Error executing Python script'));
        return;
      }
      try {
        const result = JSON.parse(stdout);
        console.log('Python script result:', result); // Log result for debugging
        resolve(result);
      } catch (e) {
        console.error('Error parsing JSON:', e);
        reject(new Error('Error parsing JSON output from Python script'));
      }
    });
  });
}