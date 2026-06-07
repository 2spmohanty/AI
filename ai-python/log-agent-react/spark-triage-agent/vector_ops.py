import re
import chromadb
#from chromadb.utils import embedding_functions
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
import os

load_dotenv()
# Initialize clean persistent vector tracking using free HuggingFace embeddings locally
print("Establishing chroma vector")
chroma_client = chromadb.PersistentClient(path="../emr_vector_store")
print("Instantiating HF Sentence Transformer models")
'''
hf_embedding_fn = embedding_functions.HuggingFaceEmbeddingFunction(
    api_key=os.getenv("HF_TOKEN"),  # Local execution doesn't strictly validate this for basic setups
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)
# Not able to establish connection so downloadng the model locally
'''
hf_embedding_fn = SentenceTransformerEmbeddingFunction(
    model_name="sentence-transformers/all-MiniLM-L6-v2"  # Downloads & runs locally
)

print("Creating/Getting Chroma CLient...")
collection = chroma_client.get_or_create_collection(name="spark_errors", embedding_function=hf_embedding_fn,
                                                    metadata={
                                                        "hnsw:space": "cosine",
                                                        # Changes distance metric from default L2 to Cosine similarity
                                                        "hnsw:construction_ef": 200
                                                        # Increases indexing accuracy during your ingestion runs
                                                    })


def parse_log(log_file: str) -> list[dict]:
    """Chunks logs with LangChain API, filtering out INFO noise."""
    print(f"Chunking log file  : {log_file} ")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        separators=["\n", " | ", " "]
    )
    CRITICAL_KEYWORDS = {"error", "warning", "warn", "traceback", "exception", "failed", "fatal"}

    with open(log_file, 'r', encoding='utf-8') as f:
        raw_content = f.read()

    if not any(kw in raw_content.lower() for kw in CRITICAL_KEYWORDS):
        return []

    langchain_docs = text_splitter.create_documents([raw_content])
    chromadb_candidates = []

    ts_pattern = re.compile(r'\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}')
    level_pattern = re.compile(r'\b(ERROR|WARN|WARNING|FATAL)\b', re.IGNORECASE)

    for idx, doc in enumerate(langchain_docs):
        chunk_text = doc.page_content.strip()
        if any(kw in chunk_text.lower() for kw in CRITICAL_KEYWORDS):
            ts_match = ts_pattern.search(chunk_text)
            level_match = level_pattern.search(chunk_text)

            timestamp = ts_match.group(0) if ts_match else "2026-01-01 00:00:00"
            log_level = level_match.group(0).upper() if level_match else "ERROR"

            chromadb_candidates.append({
                "id": f"chunk_{timestamp.replace(' ', '_').replace(':', '-')}_{idx}",
                "document": chunk_text,
                "metadata": {"timestamp": timestamp, "level": log_level, "source": log_file}
            })
    return chromadb_candidates


def query_vector_store(query_text: str, n_results: int = 2) -> list[str]:
    """Queries ChromaDB for similar past logs to establish structural context."""
    results = collection.query(query_texts=[query_text], n_results=n_results)
    return [doc for sublist in results.get('documents', []) for doc in sublist]
