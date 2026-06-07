import {openai_client, subase_client} from '../config.js';
import {getPodCastSearchTool } from './embedding_master.js'

const chatMessage = [{
    role: "system",
    content: `You are a Podcast enthusiast. You have to give suggestion based on exactly 2 information
    provided to you. A question and a context. Do not make up anything. If you dont know the answer or
     dont have the context, say you answer with, say dont know.`
    
}]

async function getChatCompletion(userQuery, contextData) {
    try {
        chatMessage.push({
        role: "user",
        content:  `Question: ${userQuery}. Context: ${contextData}`})
        console.log(`Context Data: ${contextData}`)

        const response = await openai_client.chat.completions.create({
            model: process.env.AI_MODEL,
            messages: chatMessage
        })
        console.log(response.choices[0].message.content)
    } catch (error) {
        console.log("context_chaining.js", " :: chat() :: Error ❌ : ", error)
    }
}

async function getChatCompletionStream(userQuery, contextData) {
    try {
        chatMessage.push({
        role: "user",
        content:  `Question: ${userQuery}. Context: ${contextData}`})
        console.log(`Context Data: ${contextData}`)

        const stream = await openai_client.chat.completions.create({
            model: process.env.AI_MODEL,
            messages: chatMessage,
            stream: true
        })
        process.stdout.write("Thinking... ");
        for await(const chunk of stream){
            const content = chunk.choices[0]?.delta?.content || ""
            process.stdout.write(content);
        }

    } catch (error) {
        process.stdout.write("context_chaining.js", " :: chat() :: Error ❌ : ", error);
    }
}


async function chat(query){
    console.log(" Analysing  user Input....")   
    const matchedData = await getPodCastSearchTool(query)
    console.log("Thinking .....")
    //await getChatCompletion(query,matchedData) 
    await getChatCompletionStream(query,matchedData)
    

}

const userQuestion = "What do you think Elon Musk would like to listen to?"

await chat(userQuestion)