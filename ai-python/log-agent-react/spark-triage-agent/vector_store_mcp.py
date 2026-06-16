from fastmcp import FastMCP
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from dotenv import load_dotenv


load_dotenv()
# Initialize clean persistent vector tracking using free HuggingFace embeddings locally
print("Establishing chroma vector")
chroma_client = chromadb.PersistentClient(path="../emr_vector_store")
print("Instantiating HF Sentence Transformer models")


# Initialize FastMCP
mcp = FastMCP("RemoteDataEngine")

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



@mcp.tool
def query_vector_store(query_text: str, n_results: int = 2) -> list[str]:
    """Queries ChromaDB for similar past logs to establish structural context."""
    results = collection.query(query_texts=[query_text], n_results=n_results)
    return [doc for sublist in results.get('documents', []) for doc in sublist]


if __name__ == "__main__":
    # Tells FastMCP to boot an HTTP server on port 8000 instead of standard local I/O
    mcp.run(transport="streamable-http", host="0.0.0.0", port=9090)
