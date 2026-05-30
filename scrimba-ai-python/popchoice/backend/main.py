"""
PopChoice — FastAPI Backend
"""

import os
import json
import time
import logging
import inspect
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(funcName)-35s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("popchoice")


def log(msg: str, level: str = "info"):
    """Log with the caller name."""
    frame = inspect.stack()[1]
    caller = frame.function
    record = logging.LogRecord(
        name="popchoice",
        level=getattr(logging, level.upper()),
        pathname=frame.filename,
        lineno=frame.lineno,
        msg=msg,
        args=(),
        exc_info=None,
        func=caller,
    )
    logger.handle(record)


# ── APP ───────────────────────────────────────────────────────────────────────

app = FastAPI(title="PopChoice API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic model definition

class PersonTaste(BaseModel):
    name: str
    favourite_movie: str
    mood: str
    vibe: str


class MovieNightRequest(BaseModel):
    duration_minutes: int
    people: List[PersonTaste]


class Movie(BaseModel):
    title: str
    description: str
    image_url: Optional[str] = None
    year: Optional[str] = None
    genre: Optional[str] = None
    duration: Optional[str] = None
    match_reason: str


class MovieNightResponse(BaseModel):
    suggestions: List[Movie]


# Prompt helper methd

def build_group_taste_prompt(request: MovieNightRequest) -> str:
    log(f"Building taste prompt for {len(request.people)} people | duration: {request.duration_minutes} min")
    lines = [f"Movie night duration: {request.duration_minutes} minutes."]
    lines.append(f"Number of people: {len(request.people)}")
    lines.append("")
    for i, person in enumerate(request.people, 1):
        lines.append(f"Person {i} ({person.name}):")
        lines.append(f"  Favourite movie: {person.favourite_movie}")
        lines.append(f"  Mood: {person.mood}")
        lines.append(f"  Vibe: {person.vibe}")
    prompt = "\n".join(lines)
    log(f"Prompt built — {len(prompt)} chars")
    return prompt


# Vector client

def get_supabase_client():
    from supabase import create_client
    log("Initialising Supabase client")
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        log("SUPABASE_URL or SUPABASE_KEY not set in environment", "error")
        raise ValueError("Supabase credentials missing")
    client = create_client(url, key)
    log("Supabase client ready")
    return client


# embeding fetching

async def get_embedding(text: str) -> List[float]:
    from openai import AsyncOpenAI
    model = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
    log(f"Requesting embedding | model: {model} | input length: {len(text)} chars")
    t = time.perf_counter()
    client = AsyncOpenAI(api_key=os.getenv("AI_KEY"))
    result = await client.embeddings.create(model=model, input=text)
    elapsed = time.perf_counter() - t
    embedding = result.data[0].embedding
    log(f"Embedding received | dim: {len(embedding)} | elapsed: {elapsed:.2f}s")
    return embedding


async def search_movies_by_embedding(embedding: List[float], limit: int = 10) -> List[dict]:
    log(f"Calling match_choices RPC | threshold: 0.7 | limit: {limit}")
    t = time.perf_counter()
    supabase = get_supabase_client()
    result = supabase.rpc("match_choices", {
        "query_embedding": embedding,
        "match_threshold": 0.7,
        "match_count": limit
    }).execute()
    elapsed = time.perf_counter() - t
    candidates = result.data or []
    log(f"Supabase returned {len(candidates)} candidates | elapsed: {elapsed:.2f}s")
    for c in candidates:
        log(f"  Candidate: '{c.get('title')}' | similarity: {c.get('similarity', 'n/a'):.4f}")
    return candidates


# chat completion

async def get_final_recommendations(
    group_taste: str,
    candidate_movies: List[dict]
) -> List[Movie]:
    from openai import AsyncOpenAI

    model = os.getenv("AI_MODEL", "gpt-4o")
    log(f"Requesting recommendations | model: {model} | candidates: {len(candidate_movies)}")

    if not candidate_movies:
        log("No candidates from vector search — returning empty list", "warning")
        return []

    system_prompt = """You are a movie recommendation expert.

STRICT RULES:
1. Only select movies from the candidate list provided. Never suggest a movie not in the list.
2. Select between 3 and 5 movies that best match the group's collective taste.
3. match_reason must reference each person by name and explain why this movie fits their stated taste.
4. description must come from the candidate content field only. Do not invent plot details.
5. If no candidates are relevant, return an empty suggestions list.
6. If you lack sufficient information for a confident match, set match_reason to:
   'I lack the information for this taste profile and will need more data to recommend confidently.'"""

    client = AsyncOpenAI(api_key=os.getenv("AI_KEY"))
    t = time.perf_counter()

    response = await client.responses.parse(
        model=model,
        instructions=system_prompt,
        input=f"Group taste:\n{group_taste}\n\nCandidate movies:\n{json.dumps(candidate_movies, indent=2)}",
        text_format=MovieNightResponse
    )

    elapsed = time.perf_counter() - t
    selections = response.output_parsed.suggestions
    log(f"OpenAI response received | elapsed: {elapsed:.2f}s | selected: {len(selections)} movies")

    candidates_by_title = {m["title"]: m for m in candidate_movies}

    movies = [
        Movie(
            title=s.title,
            description=s.description,
            match_reason=s.match_reason,
            year=s.year,
            genre=s.genre,
            duration=s.duration,
            image_url=candidates_by_title.get(s.title, {}).get("image_url")
        )
        for s in selections
    ]

    for m in movies:
        log(f"  Selected: '{m.title}' | image: {'yes' if m.image_url else 'no'}")

    return movies


# routes

@app.get("/health")
async def health():
    log("Health check")
    return {"status": "ok", "service": "PopChoice API", "timestamp": datetime.utcnow().isoformat()}


@app.post("/recommend", response_model=MovieNightResponse)
async def recommend(request: MovieNightRequest):
    request_id = datetime.utcnow().strftime("%H%M%S%f")
    log(f"[{request_id}] Incoming request | people: {len(request.people)} | duration: {request.duration_minutes} min")
    total_start = time.perf_counter()

    if len(request.people) < 1:
        raise HTTPException(status_code=400, detail="At least 1 person required")
    if len(request.people) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 people allowed")

    # build group taste prompt
    log(f"[{request_id}] building group taste prompt")
    group_taste = build_group_taste_prompt(request)

    # embed group taste
    log(f"[{request_id}] Fetching — embedding group taste")
    t = time.perf_counter()
    embedding = await get_embedding(group_taste)
    log(f"[{request_id}] Fetching complete | {time.perf_counter()-t:.2f}s")

    #  vector search Supabase
    log(f"[{request_id}] Matching — Searching Vector DB")
    t = time.perf_counter()
    candidates = await search_movies_by_embedding(embedding, limit=10)
    log(f"[{request_id}] Search complete | {len(candidates)} candidates | {time.perf_counter()-t:.2f}s")

    # chat completion structired output
    log(f"[{request_id}] Initiating — call OpenAI for recommendations")
    t = time.perf_counter()
    movies = await get_final_recommendations(group_taste, candidates)
    log(f"[{request_id}] Recommendation complete | {len(movies)} movies | {time.perf_counter()-t:.2f}s")

    total_elapsed = time.perf_counter() - total_start
    log(f"[{request_id}] Total TIme | total: {total_elapsed:.2f}s")

    return MovieNightResponse(suggestions=movies)


@app.get("/movies/sample", response_model=MovieNightResponse)
async def sample_movies():
    log("Returning sample movies")
    return MovieNightResponse(suggestions=[
        Movie(
            title="Interstellar",
            description="A team of explorers travel through a wormhole in space in an attempt to ensure humanity's survival.",
            image_url="https://image.tmdb.org/t/p/original/gEU2QniE6E77NI6lCU6MxlNBvIe.jpg",
            year="2014",
            genre="Sci-Fi / Drama",
            duration="169 min",
            match_reason="Matches your group's love of thought-provoking cinema and epic storytelling."
        ),
        Movie(
            title="The Grand Budapest Hotel",
            description="The adventures of Gustave H, a legendary concierge at a famous European hotel.",
            image_url="https://image.tmdb.org/t/p/original/eWdyYQreja6JGCzqHWXpWHDrrPo.jpg",
            year="2014",
            genre="Comedy / Drama",
            duration="99 min",
            match_reason="Perfect blend of fun and substance — great for a mixed-mood group."
        ),
        Movie(
            title="Parasite",
            description="Greed and class discrimination threaten the newly formed symbiotic relationship between two families.",
            image_url="https://image.tmdb.org/t/p/original/7IiTTgloJzvGI1TAYymCfbfl3vT.jpg",
            year="2019",
            genre="Thriller / Drama",
            duration="132 min",
            match_reason="A modern classic that satisfies both serious and fun viewing preferences."
        ),
    ])