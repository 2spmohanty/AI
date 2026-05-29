import OpenAI from 'openai';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';
import { createClient } from '@supabase/supabase-js'; 

// 1. Get the current directory path of config.js
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// 2. Point precisely to the root folder's .env file
dotenv.config({ path: path.resolve(__dirname, '../../.env') });


/** Ensure the OpenAI API key is available and correctly configured */
if (!process.env.OPENAI_API_KEY) {
    throw new Error("OpenAI API key is missing or invalid.");
}

if (!process.env.SUPABASE_URL || !process.env.SUPABASE_KEY) {
    throw new Error("Supabase URL or Service Role Key is missing or invalid");
}


/** OpenAI config */
export const openai_client =  new OpenAI({
    apiKey: process.env.OPENAI_API_KEY
});

export const subase_client = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_KEY, {
  auth: { persistSession: false },
});
