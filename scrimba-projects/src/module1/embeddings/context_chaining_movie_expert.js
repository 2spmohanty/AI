import {openai_client} from '../config.js';
import {getMovieSearchTool} from './embedding_master.js'

const SYSTEM_PROMPT = {
    role: "system",
    content: `You are an enthusiastic movie expert who loves recommending movies to people. You will be given two pieces of information - some context about movies and a question. Your main job is to formulate a short answer to the question using the provided context. If the answer is not given in the context, find the answer in the conversation history if possible. If you are unsure and cannot find the answer, say, "Sorry, I don't know the answer." Please do not make up the answer.`
};

async function getChatCompletion(userQuery, contextData) {
    try {
        const localMessages = [
            SYSTEM_PROMPT,
            {
                role: "user",
                content: `Question: ${userQuery}. Context: ${contextData}`
            }
        ];

        const response = await openai_client.chat.completions.create({
            model: process.env.AI_MODEL,
            messages: localMessages
        })
        console.log(response.choices[0].message.content)
    } catch (error) {
        console.log("context_chaining.js", " :: chat() :: Error ❌ : ", error)
    }
}

async function getChatCompletionStream(userQuery, contextData) {
    try {
        const localMessages = [
            SYSTEM_PROMPT,
            {
                role: "user",
                content: `Question: ${userQuery}. Context: ${contextData}`
            }
        ];
        //console.log(`Context Data: ${contextData}`)

        const stream = await openai_client.chat.completions.create({
            model: process.env.AI_MODEL,
            messages: localMessages, // Use local array
            stream: true
        });

        
        for await(const chunk of stream){
            const content = chunk.choices[0]?.delta?.content || ""
            process.stdout.write(content);
        }
         process.stdout.write("\n");

    } catch (error) {
        process.stdout.write("context_chaining.js", " :: chat() :: Error ❌ : ", error);
    }
}


async function chat(query){
    console.log(" Analysing  user Input....")   
    const matchedData = await getMovieSearchTool(query)
    console.log("Thinking .....")
    //await getChatCompletion(query,matchedData) 
    await getChatCompletionStream(query,matchedData)
    

}

const userQuestion = "Which movie will be a feel good to watch?"

await chat(userQuestion)