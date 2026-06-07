import OpenAI from "openai"
import { getCurrentWeather, getLocation, tools } from "./tools.js"
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

dotenv.config({ path: path.resolve(__dirname, '../../../.env') });


export const openai = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY,
    dangerouslyAllowBrowser: true
})

const availableFunctions = {
    getCurrentWeather,
    getLocation
}

async function agent(query) {
    const messages = [
        { role: "system", content: "You are a helpful AI agent. Give highly specific answers based on the information you're provided. Prefer to gather information with the tools provided to you rather than giving basic, generic answers." },
        { role: "user", content: query }
    ]

    const MAX_ITERATIONS = 5

    // for (let i = 0; i < MAX_ITERATIONS; i++) {
    //     console.log(`Iteration #${i + 1}`)
        const response = await openai.chat.completions.create({
            model: process.env.AI_MODEL,
            messages,
            tools
        })

        console.log(response.choices[0])
        const { finish_reason: finishReason, message } = response.choices[0]
        
        if (finishReason === "stop") {
            console.log(message.content)
            console.log("AGENT ENDING")
            return
        }else if (finishReason === "tool_calls"){
            messages.push(message)

            for (const toolCall of message.tool_calls) {
                const functionName = toolCall.function.name
                
                const functionToCall = availableFunctions[functionName]
                const argsToPass = JSON.parse(toolCall.function.arguments)
                const functionResult = await functionToCall()

                console.log(`Function [${functionName}] responded with:`, functionResult)
                messages.push({
                    role: "tool",
                    tool_call_id: toolCall.id,
                    name: functionName,
                    content: JSON.stringify(functionResult) 
                })
            }

        }
        

    // }
}


console.log(process.env.AI_MODEL)

async function modern_agent(query) { 
    // First Call: Initialize the agent sequence
    let response = await openai.responses.create({ 
        model: process.env.AI_MODEL, 
        instructions: "You are a helpful AI agent. Use tools to give highly specific answers.", 
        input: query, 
        tools: tools, 
        parallel_tool_calls: false 
    });

    // Loop continuously as long as the model requests tools
    while (response.tool_calls?.length > 0) { 
        const toolOutputs = []; 
        
        for (const toolCall of response.tool_calls) { 
            const name = toolCall.function.name; 
            const args = JSON.parse(toolCall.function.arguments);
            const result = await availableFunctions[name](args); 
            
            toolOutputs.push({ 
                tool_call_id: toolCall.id, 
                output: typeof result === 'string' ? result : JSON.stringify(result) 
            }); 
        } 

        // Send tool updates back to the same sequence ID and re-evaluate
        response = await openai.responses.create({ 
            model: process.env.AI_MODEL, 
            previous_response_id: response.id, 
            tool_outputs: toolOutputs 
        }); 
    } 

    // Return the finalized summary once all tools are complete
    return response.output_text; 
}

const answer = await modern_agent("What is the current weather? Check my location first.");
console.log(answer);
