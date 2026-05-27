import OpenAI from 'openai';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

// 1. Get the current directory path of config.js
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// 2. Point precisely to the root folder's .env file
dotenv.config({ path: path.resolve(__dirname, '../../.env') });


/** Ensure the OpenAI API key is available and correctly configured */
if (!process.env.OPENAI_API_KEY) {
    throw new Error("OpenAI API key is missing or invalid.");
}



/** OpenAI config */
export default new OpenAI({
    apiKey: process.env.OPENAI_API_KEY,
    dangerouslyAllowBrowser: true
});