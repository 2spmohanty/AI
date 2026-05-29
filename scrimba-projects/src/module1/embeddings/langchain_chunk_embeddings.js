import { openai, supabase } from '../config.js';
import {RecursiveCharacterTextSplitter} from "@langchain/textsplitters";

import { readFile } from 'fs/promises';
import { join } from 'path';
import { fileURLToPath } from 'url';
const __dirname = fileURLToPath(new URL('.', import.meta.url));

async function loadLocalData(documentName){
  console.log(`Loading Documents from Local: ${documentName}`)
    try {
            
            const filePath = join(__dirname, documentName);
            
            
            const text = await readFile(filePath, 'utf8');
            
            
            return text;
            
        } catch (error) {
            console.error("Failed to read documentName:", error.message);
        }
}

async function getTextEmbeddings(text) {

    const embed_model = "text-embedding-ada-002"

    const embeddingObj = await openai.embeddings.create({
        model: embed_model,
        input: text
    });  

    return embeddingObj.data[0].embedding
    
}

async function loadData(documentName){
    console.log(`Loading Documents from Network: ${documentName}`)
    const response = await fetch(documentName, 'utf8'); 
    if (!response.ok) throw new Error(`Failed to fetch ${documentName}`);
    const data = await response.text()
    return data; 
}
/* Split movies.txt into text chunks.
Return LangChain's "output" – the array of Document objects. */

async function splitDocument(documentName) {

    console.log("Split Document In Progress")
    const data = await loadLocalData(documentName)
    if (!data) return [];
    
    try {
      const splitter = new RecursiveCharacterTextSplitter({
      chunkSize: 190,
      chunkOverlap: 25
      });
      const chunks = await splitter.splitText(data)

      return chunks

    } catch (error) {
        console.error("langchain_chunk_embeddings.js", " :: splitDocument() :: Error ❌ : ", error);
    }
    
}

/* Create an embedding from each text chunk.
Store all embeddings and corresponding text in Supabase. */
async function createAndStoreEmbeddings() {

  try{
      console.log("Chunking Document using Langchain")
      const chunkData = await splitDocument("movies.txt");

      console.log("Generating Embeddings using Open AI")
      const movieDataEmbeddings = await Promise.all(

      chunkData.map(async (chunk) => {
        const movieEmbedding = await getTextEmbeddings(chunk);
        return {
          movie_data: chunk,
          embedding: movieEmbedding
        }
      })

        )
      
      console.log("Inserting to Supabase Vector")
      const { data, error } = await supabase
          .from("movies")
          .insert(movieDataEmbeddings);

      if (error) throw error;
      console.log("Embeddings successfully stored.");

  }catch(error){
    console.error("Error creating or storing embeddings: ", error);
  }
   
}

createAndStoreEmbeddings();