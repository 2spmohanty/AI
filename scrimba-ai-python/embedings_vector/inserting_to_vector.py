from openai import AsyncOpenAI
import asyncio
from dotenv import load_dotenv
import os
from supabase import create_client, Client

load_dotenv()

api_key = os.getenv("AI_KEY")
ai_url = os.getenv("AI_URL")

podcasts =  [
  "Beyond Mars (1 hr 15 min): Join space enthusiasts as they speculate about extraterrestrial life and the mysteries of distant planets.",
  "Jazz under stars (55 min): Experience a captivating night in New Orleans, where jazz melodies echo under the moonlit sky.",
  "Mysteries of the deep (1 hr 30 min): Dive with marine explorers into the uncharted caves of our oceans and uncover their hidden wonders.",
  "Rediscovering lost melodies (48 min): Journey through time to explore the resurgence of vinyl culture and its timeless appeal.",
  "Tales from the tech frontier (1 hr 5 min): Navigate the complex terrain of AI ethics, understanding its implications and challenges.",
  "The soundscape of silence (30 min): Traverse the globe with sonic explorers to find the world's most serene and silent spots.",
  "Decoding dreams (1 hr 22 min): Step into the realm of the subconscious, deciphering the intricate narratives woven by our dreams.",
  "Time capsules (50 min): Revel in the bizarre, endearing, and profound discoveries that unveil the quirks of a century past.",
  "Frozen in time (1 hr 40 min): Embark on an icy expedition, unearthing secrets hidden within the majestic ancient glaciers.",
  "Songs of the Sea (1 hr): Dive deep with marine biologists to understand the intricate whale songs echoing in our vast oceans."
]

openai_client = AsyncOpenAI(api_key=api_key)

async def get_embeddings(text):
    embed_result = await openai_client.embeddings.create(
            model="text-embedding-ada-002",
            input=text,
    )
    return embed_result.data[0].embedding

async def main():

    tasks = [get_embeddings(content) for content in podcasts]
    embeddings = await asyncio.gather(*tasks)
    print("Obtained Vectors, Zipping Results.")
    vector_data = [{"content": text, "embedding": embed} for text, embed in zip(podcasts, embeddings)]
    print("Preparing Database for Inserts")
    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_KEY")


    supabase: Client = create_client(url, key)
    print("Connected to Supabase.")
    try:
        # Execute the bulk insertion
        print("Target API Path:", supabase.supabase_url)
        response = supabase.table("documents").insert(vector_data).execute()
        print("Successfully inserted rows:", response.data)
    except Exception as e:
        print("Error inserting rows:", e)






if __name__ == "__main__":
    asyncio.run(main())

