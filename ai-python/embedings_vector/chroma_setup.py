import chromadb
from data.simialrity_search_data import sentences
import os
from dotenv import load_dotenv
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

load_dotenv()
client = chromadb.PersistentClient(path="./chroma_db")

openai_ef = OpenAIEmbeddingFunction(
    api_key=os.getenv("AI_KEY"),
    model_name="text-embedding-3-small"
)

collection = client.create_collection(name="test_collection",
                                      embedding_function=openai_ef,
                                      configuration={
                                          "hnsw": {
                                              "space": "cosine",
                                              "ef_construction": 200
                                          }
                                      }
                                      )

collection.add(
    documents=sentences,
    ids=[f"doc_{i}" for i in range(len(sentences))],

)

results = collection.query(
    query_texts=["interest rates and inflation"],
    n_results=3
)
print(results["documents"])
