import 'dotenv/config';
import OpenAI from "openai";

console.log("Model:", process.env.VITE_OPENAI_MODEL);

const client = new OpenAI({
    apiKey: process.env.AI_KEY ,
    baseURL: process.env.AI_URL    
});

const userPrompt = `You are a story teller who tells a random story.
The story should be maximum within 100 words but should be on office politics.
The tone is British Humour and savage dealing with a Tech dump Tech Lead, who ask status based on Jira tickets.`;

const userMessage = {
    role: "user",
    content: userPrompt // Removed quotes here
};

console.log("Established connection. Requesting story...");

const response = await client.chat.completions.create({
    model: process.env.AI_MODEL,
    messages: [userMessage],
    max_completion_tokens: 256
});

// To see just the story text:
console.log(response.choices[0].message.content);
