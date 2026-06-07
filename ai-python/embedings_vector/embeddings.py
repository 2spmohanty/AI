import json

from openai import AsyncOpenAI
from dotenv import load_dotenv
import os
import sys
load_dotenv()
import asyncio

client = AsyncOpenAI(api_key=os.getenv("AI_KEY"))

#movie_file = "/Users/smruti/Dev/2spmohanty/AI/scrimba-ai-python/popchoice/ai/data/movies_enriched.json"

#movie_data = json.load(open(movie_file))

sentences = [
    # Financial
    "The stock market crashed today",
    "Investors lost billions in the selloff",
    "Central banks raised interest rates",
    "Inflation hit a 40-year high this quarter",
    "Tech stocks recovered after Fed announcement",
    # Weather
    "The weather is sunny and warm",
    "Heavy rainfall caused flooding in the city",
    "Temperature dropped below zero overnight",
    "Heatwave warnings issued across the country",
    "Snow is expected across northern regions",
    # Food
    "I love eating pizza on Fridays",
    "The pasta was perfectly al dente",
    "Best sushi restaurant in the city",
    "Homemade bread fresh out of the oven",
    "Coffee in the morning makes everything better",
    # Sports
    "The team won the championship last night",
    "Player injured during final quarter",
    "Record broken at the Olympic games",
    "Coach resigned after poor season",
    "Transfer fee hit 100 million dollars",
]

async def get_embedding(text):
    result = await client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    )
    return result.data[0].embedding


async def get_all_embeddings(text_list):

    tasks = [get_embedding(sentence) for sentence in text_list]
    result =  await asyncio.gather(*tasks)
    for sentence, embedding in zip(text_list, result):
        print("^"*10)
        print(sentence)
        print(f"Dimensions: {len(embedding)}")
        print(f"First 5 values: {embedding[:5]}")
        print("$" * 10)



if __name__ == "__main__":
    asyncio.run(get_all_embeddings(sentences))