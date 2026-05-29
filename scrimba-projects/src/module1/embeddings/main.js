import {openai_client} from '../config.js';

const content = [
  "Beyond Mars: speculating life on distant planets.",
  "Jazz under stars: a night in New Orleans' music scene.",
  "Mysteries of the deep: exploring uncharted ocean caves.",
  "Rediscovering lost melodies: the rebirth of vinyl culture.",
  "Tales from the tech frontier: decoding AI ethics.",
]; 

/*
  Challenge: Pair text with its embedding
    - For each text input, create an object with 
      a 'content' and 'embedding' property
    - The value of 'content' should be the text
    - The value of 'embedding' should be the vector embedding for that text
*/

async function getEmbedding(text){
  const result = await openai_client.embeddings.create({
    model: "text-embedding-ada-002",
    input: text,
  });
  return result.data[0].embedding
}
async function main() {
  
  const embeddingsPromisses = content.map( async item => ({
    'content' : item,
    'embedding' : await getEmbedding(item)
  }))

  const result = await Promise.all(embeddingsPromisses);

  console.log(result);
}
main();