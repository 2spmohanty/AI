from openai import AsyncOpenAI
import asyncio
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("AI_KEY")
ai_url = os.getenv("AI_URL")

contents = [
    "Beyond Mars: speculating life on distant planets.",
    "Jazz under stars: a night in New Orleans' music scene.",
    "Mysteries of the deep: exploring uncharted ocean caves.",
    "Rediscovering lost melodies: the rebirth of vinyl culture.",
    "Tales from the tech frontier: decoding AI ethics.",
]

openai_client = AsyncOpenAI(api_key=api_key)

async def get_embeddings(text):
    embed_result = await openai_client.embeddings.create(
            model="text-embedding-ada-002",
            input=text,
    )
    return embed_result.data[0].embedding

async def main():

    tasks = [get_embeddings(content) for content in contents]
    embeddings = await asyncio.gather(*tasks)
    result = [{"content": text, "embedding": embed} for text, embed in zip(contents, embeddings)]

    print(result)


if __name__ == "__main__":
    asyncio.run(main())

