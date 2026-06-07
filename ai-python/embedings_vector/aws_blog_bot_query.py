import chromadb
import os
from dotenv import load_dotenv
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
import json

load_dotenv()

client = chromadb.PersistentClient(path="./chroma_db")

openai_ef = OpenAIEmbeddingFunction(
    api_key=os.getenv("AI_KEY"),
    model_name="text-embedding-3-small"
)

collection = client.get_or_create_collection(name="aws_collection",
                                      embedding_function=openai_ef,
                                      configuration={
                                          "hnsw": {
                                              "space": "cosine",
                                              "ef_construction": 200
                                          }
                                      }
                                      )


queries = [
    "machine learning and AI services",
    "cost optimisation and savings",
    "security and compliance",
    "serverless and Lambda",
    "database and storage solutions",
    "networking and VPC",
    "container and Kubernetes",
    "data analytics and Athena",
    "disaster recovery and backup",
    "developer tools and CI/CD"
]

result = collection.query(
    query_texts=queries,
    n_results=2
)

for i, (aws_ids, documents, metadatas) in enumerate(zip(result["ids"], result["documents"], result["metadatas"])):
    print(f"\nQuery: {queries[i]}")
    print("─" * 40)
    for aws_id, document, metadata in zip(aws_ids, documents, metadatas):
        print(f"  Title: {metadata['title']}")
        print(f"  URL:   {metadata['url']}")
        print()
