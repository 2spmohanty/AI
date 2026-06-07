
#  Embeddings & Vector Databases

![AWS RAG Demo](screenshots/embedded.gif)

---

## What I built

### 1. Embeddings from scratch
Generated embeddings using OpenAI `text-embedding-3-small` SDK directly in Python.
Verified 1536 dimensions per vector. Embedded 20 sentences across 4 topic clusters — financial, weather, food, sports.

### 2. Cosine similarity heatmap
Computed a 20×20 cosine similarity matrix across all sentence pairs.
Visualised as a heatmap with matplotlib — clear block patterns emerged showing the model groups semantically related sentences together even without explicit labels.


**Key observation:** Financial sentences clustered together, weather sentences clustered together — the model understood topic relationships purely from text meaning, no keyword overlap required.

### 3. Vector arithmetic
Tested the classic `King − Man + Woman ≈ Queen` analogy on `text-embedding-3-small`.
Result: `0.616` similarity — lower than the word2vec benchmark because `text-embedding-3-small` is optimised for sentence-level semantic similarity, not word-level analogy completion.

**Key learning:** Embedding models are not interchangeable. Choose based on the task — sentence similarity models for RAG and search, word-level models for analogy tasks.

### 4. Chroma local vector database
Set up ChromaDB with persistent storage and cosine similarity space.
Configured HNSW index with `ef_construction=200` for better recall.
Added 20 sentences with OpenAI embedding function — Chroma handles embedding automatically at query time.

### 5. AWS blog posts — semantic search
Fetched 20 real AWS blog posts from the AWS RSS feed.
Embedded and stored in a persistent Chroma collection with title and URL as metadata.
Ran 10 domain-specific queries covering ML, security, serverless, networking, containers, analytics.

### 6. Semantic vs keyword search comparison
Ran the same queries through semantic search (Chroma) and keyword search (word overlap).

**Finding:** Keyword search matches exact words — works when terminology is precise. Semantic search understands intent — finds relevant results even when exact terms don't appear. For "cost optimisation and savings", semantic search returned a prompt optimisation article (understanding the cost relationship) while keyword search returned an unrelated weekly roundup that happened to match 2 common words.

### 7. RAG pipeline over AWS Well-Architected Framework PDF
Full end-to-end RAG system:
- Loaded 100+ page PDF with `pypdf`
- Chunked each page into 500-character chunks with 50-character overlap
- Parallel batch ingestion into Chroma using `ThreadPoolExecutor` (4 workers, 100 chunks per batch)
- Async query with `asyncio` and `run_in_executor` for non-blocking Chroma calls
- Streaming GPT-4o-mini response with page-cited architectural answers

**System prompt:** Principal AWS Cloud Solutions Architect persona with structured output — Executive Summary, Architectural Recommendations with page citations, Design Justification.



### 8. PopChoice — Chroma backend
Added a local Chroma alternative to the Supabase vector search in the PopChoice movie recommender backend.
Pre-computed embedding passed directly as `query_embeddings` — no re-embedding inside the search function.
Full local stack: Streamlit frontend → FastAPI backend → Chroma → GPT-4o-mini → movie recommendations, no cloud database required.

---

## Skills gained

| Skill | Detail |
|-------|--------|
| Embedding generation | OpenAI SDK, batch input, 1536-dim vectors |
| Cosine similarity | Manual implementation with numpy |
| Heatmap visualisation | matplotlib `imshow`, similarity matrix |
| Vector arithmetic | King−Man+Woman, understanding model limitations |
| ChromaDB | Persistent client, HNSW config, cosine space, metadata |
| Semantic search | `query_texts` vs `query_embeddings` |
| Keyword search | Word overlap baseline, comparison methodology |
| PDF ingestion | pypdf, chunking with overlap |
| Parallel ingestion | ThreadPoolExecutor, batch strategy |
| Async RAG | asyncio, run_in_executor, streaming response |
| RAG evaluation | Comparing retrieval quality between approaches |

---

