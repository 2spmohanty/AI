import {openai_client, subase_client} from '../config.js';
import {getSearchTool } from './embedding_master.js'

const chatMessage = [{
    role: "system",
    content: `You are a Podcast enthusiasist. You have to rformulate suggestion based on 2 information
    provided to you. A question and a context. Do not make up anything. If you dont know the answer or dont have the context, say you 
    you dont know. In case at any point you see an error in Question 
    or context, tell the user that you are getting an error with the Error message and any suggestion on how to fix it.`
    
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


async function chat(query){
    console.log(" Analysing  user Input....")   
    const matchedData = await getSearchTool(query)
    console.log("Thinking .....")
    await getChatCompletion(query,matchedData) 
    

}

const userQuestion = "What do you think Elon Musk would like to listen to?"

await chat(userQuestion)