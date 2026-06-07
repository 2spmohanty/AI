import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
load_dotenv()

# Initialize local embedding function (runs on CPU/GPU via sentence-transformers)
local_embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

# Connect to database and retrieve collection
client = chromadb.PersistentClient(path="../emr_vector_store")
collection = client.get_collection(
    name="spark_errors",
    embedding_function=local_embedding_fn
)

# Minimal query execution
query_text = "Out of memory"
results = collection.query(
    query_texts=[query_text],
    n_results=2
)

# Direct raw payload dump for quick terminal debugging
print("--- RAW QUERY RESULTS ---")
print(f"IDs: {results['ids']}")
print(f"DISTANCES: {results['distances']}")
print(f"METADATAS: {results['metadatas']}")
print(f"DOCUMENTS: {results['documents']}")
