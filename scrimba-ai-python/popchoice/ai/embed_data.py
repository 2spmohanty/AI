import json
from clients import supabase_client,get_embedding, get_poster_url
import asyncio

movies = json.load(open('data/movies_enriched.json'))

def build_embed_text(movie: dict) -> str:
    return (
        f"{movie['title']} ({movie['releaseYear']}). "
        f"{movie['content']}"
    )


async def embed_and_insert(movie: dict):
    try:
        text = build_embed_text(movie)
        embedding = await get_embedding(text)

        supabase_client.table("movies").insert({
            "title": movie["title"],
            "release": int(movie["releaseYear"]),
            "content": movie["content"],
            "embedding": embedding,
            "image_url": movie.get("image_url")   # already in enriched file
        }).execute()
        print(f"Success: {movie['title']} — poster: {'yes' if movie.get('image_url') else 'none'}")
    except Exception as e:
        print(f"Failed: {movie['title']} — {e}")
        

async def embed_movies():
    batch_size = 10
    for i in range(0, len(movies), batch_size):
        batch = movies[i:i + batch_size]
        print(f"Processing batch {i // batch_size + 1} — {len(batch)} movies")
        await asyncio.gather(*[embed_and_insert(m) for m in batch])
        print(f"Batch done")

if __name__ == "__main__":
    asyncio.run(embed_movies())