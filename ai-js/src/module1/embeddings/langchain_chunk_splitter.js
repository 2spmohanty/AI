import { readFile } from 'fs/promises';
import { join } from 'path';
import { fileURLToPath } from 'url';

// 1. Get the current folder path of this script file
const __dirname = fileURLToPath(new URL('.', import.meta.url));

import {RecursiveCharacterTextSplitter} from "@langchain/textsplitters"

async function loadData() {
    try {
        
        const filePath = join(__dirname, 'podcasts.txt');
        
        
        const text = await readFile(filePath, 'utf8');
        
        
        return text;
        
    } catch (error) {
        console.error("Failed to read podcasts.txt:", error.message);
    }
}



async function chunkData(){
    const data = await loadData();

    if (!data) return;

    /** @type {RecursiveCharacterTextSplitter} */
    const splitter = new RecursiveCharacterTextSplitter({
        chunkSize: 150,   // Maximum number of characters per chunk
        chunkOverlap: 15, // Number of characters to overlap between chunks
    });
    const strings = await splitter.splitText(data)

    console.log(strings)


}


chunkData()