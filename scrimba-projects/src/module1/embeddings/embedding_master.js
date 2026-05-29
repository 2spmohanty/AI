import { SupabaseClient } from '@supabase/supabase-js';
import {openai_client, subase_client} from '../config.js';

async function getTextEmbeddings(text) {

    const embed_model = "text-embedding-ada-002"

    const embeddingObj = await openai_client.embeddings.create({
        model: embed_model,
        input: text
    });

    console.log("Got Embediing Object")

    return embeddingObj.data[0].embedding
    
}

export const getSearchTool = async (queryText) => {

    
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