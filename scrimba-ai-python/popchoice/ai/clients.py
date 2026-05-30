from openai import AsyncOpenAI

from openai import AsyncOpenAI
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from typing import Optional

load_dotenv()



openai_client = AsyncOpenAI(
    api_key=os.getenv("AI_KEY")
)

supabase_client: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

import httpx

TMDB_API_KEY = os.getenv("TMDB_API_KEY")

TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/original"


async def get_poster_url(tmdb_id: int) -> Optional[str]:
    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}"
    params = {"api_key": TMDB_API_KEY}

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            poster_path = data.get("poster_path")
            if poster_path:
                return f"{TMDB_IMAGE_BASE}{poster_path}"
            return None
        except Exception as e:
            print(f"✗ TMDB fetch failed for id {tmdb_id}: {e}")
            return None


async def get_embedding(text):
    embed_result = await openai_client.embeddings.create(
            model=os.getenv("EMBEDDING_MODEL"),
            input=text,
    )
    return embed_result.data[0].embedding


