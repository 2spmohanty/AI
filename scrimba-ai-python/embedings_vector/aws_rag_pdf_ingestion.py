import os
import json
import chromadb
from pypdf import PdfReader
from dotenv import load_dotenv
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from concurrent.futures import ThreadPoolExecutor

load_dotenv()

# Client and Collection Setup
client = chromadb.PersistentClient(path="./aws_chroma_db")
openai_ef = OpenAIEmbeddingFunction(
    api_key=os.getenv("AI_KEY"),
    model_name="text-embedding-3-small"
)

collection = client.get_or_create_collection(
    name="aws_architect",
    embedding_function=openai_ef,
    configuration={
        "hnsw": {
            "space": "cosine",
            "ef_construction": 200
        }
    }
)


def load_pdf(path: str) -> list[str]:
    reader = PdfReader(path)
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text and len(text.strip()) > 50:
            pages.append(text.strip())
    return pages


def chunk_text(text: str, size: int = 500, overlap: int = 50) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        chunks.append(text[start:start + size])
        start += size - overlap
    return chunks


# Prepare data
data_file = "../data/aws/wellarchitected-framework.pdf"
data = load_pdf(data_file)
ingest_data = []

for page, data_item in enumerate(data):
    chunks = chunk_text(data_item)
    for chunk in chunks:
        ingest_data.append({"page": page, "content": chunk})

print(f"Total Chunks to be inserted: {len(ingest_data)}")


# worker function for parallel batches
def insert_batch(batch_data: list, start_idx: int):
    """Inserts a single batch into ChromaDB."""
    batch_docs = [item["content"] for item in batch_data]
    batch_meta = [{"page": item["page"]} for item in batch_data]
    batch_ids = [f"aws_{i}" for i in range(start_idx, start_idx + len(batch_data))]

    collection.add(
        documents=batch_docs,
        metadatas=batch_meta,
        ids=batch_ids
    )
    print(f"Inserted batch starting at index {start_idx}")


# Batching configuration
BATCH_SIZE = 100
MAX_WORKERS = 4  # Adjust based on CPU and OpenAI API rate limits

# batches
batches = [
    (ingest_data[i:i + BATCH_SIZE], i)
    for i in range(0, len(ingest_data), BATCH_SIZE)
]

# Execute parallel insertion
print(f"Starting parallel insertion with {MAX_WORKERS} workers...")
with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    futures = [
        executor.submit(insert_batch, batch, idx)
        for batch, idx in batches
    ]
    # ensure all threads complete
    for future in futures:
        future.result()

print("Ingestion complete")
