import chromadb
import os
from dotenv import load_dotenv
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
import json

load_dotenv()

data = json.load(open("../data/aws/aws_blogs.json"))

documents = [item["content"] for item in data]
metadata = [{"title": item["title"], "url": item["url"]} for item in data]

client = chromadb.PersistentClient(path="./chroma_db")

openai_ef = OpenAIEmbeddingFunction(
    api_key=os.getenv("AI_KEY"),
    model_name="text-embedding-3-small"
)

collection = client.create_collection(name="aws_collection",
                                      embedding_function=openai_ef,
                                      configuration={
                                          "hnsw": {
                                              "space": "cosine",
                                              "ef_construction": 200
                                          }
                                      }
                                      )

collection.add(
    documents=documents,
    ids=[f"aws_{i}" for i in range(len(documents))],
    metadatas=metadata
)
