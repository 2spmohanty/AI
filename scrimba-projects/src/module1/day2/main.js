import 'dotenv/config';
import OpenAI from "openai";
import fs from "fs/promises";

console.log("Model:", process.env.VITE_OPENAI_MODEL);

const openai = new OpenAI({
    apiKey: process.env.AI_KEY ,
    baseURL: process.env.AI_URL    
});

console.log("Established connection. Requesting story...");

export const resultSchema = {
  type: "json_schema",
  json_schema: {
    name: "buying_suggestions",
    schema: {
      type: "object",
      properties: {
        gifts: {
          type: "array",
          items: {
            type: "object",
            properties: {
              name: { type: "string" },
              price_range: { type: "string" },
              why_its_good: { type: "string" },
              buying_options: {
                type: "array",
                items: {
                  type: "object",
                  properties: {
                    business_name: { type: "string" },
                    price: { type: "string" },
                    purchase_link: { type: "string" },
                  },
                  required: ["business_name", "price", "purchase_link"],
                  additionalProperties: false,
                },
              },
            },
            required: ["name", "price_range", "why_its_good", "buying_options"],
            additionalProperties: false,
          },
        },
      },
      required: ["gifts"],
      additionalProperties: false,
    },
  },
};

const chatMessage = [{
    role: "system",
    content: `You are the Google Search for Budget Friendly .`
}];



async function logInteraction(entry) {
  await fs.appendFile(
    "./ai-log.jsonl",
    JSON.stringify({
      timestamp: new Date().toISOString(),
      ...entry,
    }) + "\n"
  );
}


async function chat(userText) {
  chatMessage.push({ role: "user", content: userText });

  const response = await openai.responses.create({
    model: process.env.AI_MODEL,
    input: chatMessage,
    tools: [
        { type: "web_search" },
    ]
  });

  const aiText = response.output_text;

  chatMessage.push({ role: "assistant", content: aiText });

  await logInteraction({
    userText,
    model: process.env.AI_MODEL,
    request: chatMessage,
    responseId: response.id,
    outputText: aiText,
    rawResponse: response,
  });

  console.log(`AI: ${aiText}`);
}

await chat("Suggest me some online options for buying Coffee Machine in Sydney, Australia.")

await chat("Where can i get best coffee beans for the above machine.")

await chat("Suggest Coffee Machine and COffee BEans that can go together.")
