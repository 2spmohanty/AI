import OpenAI from 'openai';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';
import { createClient } from '@supabase/supabase-js'; 

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

dotenv.config({ path: path.resolve(__dirname, '../../.env') });

if (!process.env.OPENAI_API_KEY) {
    throw new Error("OpenAI API key is missing or invalid.");
}

if (!process.env.SUPABASE_URL || !process.env.SUPABASE_KEY) {
    throw new Error("Supabase URL or Key is missing or invalid");
}

// 1. Initialize single instances to avoid duplicate connections
const openaiInstance = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
const supabaseInstance = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_KEY, {
  auth: { persistSession: false },
});

// 2. Assign the single instances to your preferred aliases and export them
export const openai = openaiInstance;
export const openai_client = openaiInstance;

export const supabase = supabaseInstance;
export const supabase_client = supabaseInstance;

// 3. Set your defaults (Only one default export is allowed per file)
export default openaiInstance;
