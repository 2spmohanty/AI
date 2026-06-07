import { SupabaseClient } from '@supabase/supabase-js';
import {openai_client, subase_client} from '../config.js';




async function getTextEmbeddings(text) {

    const embed_model = "text-embedding-ada-002"

    const embeddingObj = await openai_client.embeddings.create({
        model: embed_model,
        input: text
    });

    console.log("Got Embediing Onject")

    return embeddingObj.data[0].embedding
    
}

async function search(queryText) {

    
    try {
        console.log("Getting Embeddings for user text.")
        const embedding = await getTextEmbeddings(queryText);
        console.log("Fetching Matched Documents.")
        const {data: result, error: matchError} = await subase_client.rpc(
            "match_documents",{
                query_embedding : embedding,
                match_threshold: 0.3,
                match_count: 2
            }
        )
        console.log(result)
    } catch (error) {
        console.error("semantics.js", " :: search() :: Error ❌ : ", error);
    }
}

const query = "Jammin' in the Big Easy";

search(query)
