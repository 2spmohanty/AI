import json
from clients import supabase_client, get_embedding, get_poster_url
import asyncio
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from concurrent.futures import ThreadPoolExecutor
import os

movies = json.load(open('data/movies_enriched.json'))


def build_embed_text(movie: dict) -> str:
    return (
        f"{movie['title']} ({movie['releaseYear']}). "
        f"{movie['content']}"
    )


async def embed_and_insert_supabase(movie: dict):
    try:
        text = build_embed_text(movie)
        embedding = await get_embedding(text)

        supabase_client.table("movies").insert({
            "title": movie["title"],
            "release": int(movie["releaseYear"]),
            "content": movie["content"],
            "embedding": embedding,
            "image_url": movie.get("image_url")  # already in enriched file
        }).execute()
        print(f"Success: {movie['title']} — poster: {'yes' if movie.get('image_url') else 'none'}")
    except Exception as e:
        print(f"Failed: {movie['title']} — {e}")


##########################################################################


# Client and Collection Setup
client = chromadb.PersistentClient(path="../../data/chroma_db/movies_db")

openai_ef = OpenAIEmbeddingFunction(
    api_key=os.getenv("AI_KEY"),
    model_name="text-embedding-3-small"
)

collection = client.get_or_create_collection(
    name="movies_collection",
    embedding_function=openai_ef,
    configuration={
        "hnsw": {
            "space": "cosine",
            "ef_construction": 200
        }
    }
)


def build_document_metadata(movie_data_file: str) -> tuple:
    movie_data = json.load(open(movie_data_file))
    documents = []
    metadata = []
    movie_ids = []
    for idx, movie in enumerate(movie_data):
        documents.append((f"{movie['content']}"))
        metadata.append({'title': movie['title'], 'year': movie['releaseYear'], 'image_url': movie['image_url']})
        movie_ids.append(f"MOV-{idx + 1}")
    return documents, metadata, movie_ids


def embed_and_insert_chroma():
    import sys
    try:
        movie_file = "/Users/smruti/Dev/2spmohanty/AI/scrimba-ai-python/popchoice/ai/data/movies_enriched.json"
        documents, metadata, ids = build_document_metadata(movie_file)
        collection.add(ids=ids,
                       metadatas=metadata,
                       documents=documents)
        print("Successfully inserted into collection")
    except Exception as e:
        print(f"Error while inserting into collection: {e}")


##########################################################################


async def embed_movies():
    batch_size = 10
    for i in range(0, len(movies), batch_size):
        batch = movies[i:i + batch_size]
        print(f"Processing batch {i // batch_size + 1} — {len(batch)} movies")
        await asyncio.gather(*[embed_and_insert_supabase(m) for m in batch])
        print(f"Batch done")


if __name__ == "__main__":
    embed_and_insert_chroma()
    # asyncio.run(embed_movies())
