import {openai_client, supabase_client} from '../config.js';

async function getTextEmbeddings(text) {

    const embed_model = "text-embedding-ada-002"

    const embeddingObj = await openai_client.embeddings.create({
        model: embed_model,
        input: text
    });

    console.log("Got Embedding Object");

    return embeddingObj.data[0].embedding
    
}

export const getPodCastSearchTool = async (queryText) => {

    
    try {
        console.log("Getting Embeddings for user text.")
        const embedding = await getTextEmbeddings(queryText);
        console.log("Fetching Matched Documents.")
        const {data: result, error: matchError} = await subase_client.rpc(
            "match_documents",{
                query_embedding : embedding,
                match_threshold: 0.3,
                match_count: 1
            }
        )  
        if (matchError) throw matchError;  
        if (!result || result.length === 0) {
            return "No matching podcast context found.";
        }

        const searchData =   result[0].content;
        console.log(searchData)  
        return searchData 

    } catch (error) {
        return `semantics.js :: search() :: Error ❌ : ${error.message || error}`;
    }
}

export const getMovieSearchTool = async (queryText) => {

    
    try {
        console.log("Getting Embeddings for user movie query.")
        const embedding = await getTextEmbeddings(queryText);
        console.log("Fetching Matched Movies.")
        const {data: result, error: matchError} = await supabase_client.rpc(
            "match_movies",{
                query_embedding : embedding,
                match_threshold: 0.3,
                match_count: 3
            }
        )  
        if (matchError) throw matchError;  
        if (!result || result.length === 0) {
            return "No matching movie context found.";
        }

        const searchData =   result[0].movie_data;
        //console.log(searchData)  
        return searchData 

    } catch (error) {
        return `semantics.js :: search() :: Error ❌ : ${error.message || error}`;
    }
}
