import chromadb
import os
from dotenv import load_dotenv
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
import json

load_dotenv()

data = json.load(open("../data/aws/aws_blogs.json"))

documents = [item["content"] for item in data]

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

def keyword_search(query: str, documents: list, top_n: int = 2) -> list:
    query_words = set(query.lower().split())
    scores = []
    for i, doc in enumerate(documents):
        doc_words = set(doc.lower().split())
        score = len(query_words & doc_words)  # word overlap count
        scores.append((score, i, doc))
    scores.sort(reverse=True)
    return scores[:top_n]


test_queries = [
    "serverless and Lambda",
    "cost optimisation and savings"
]

for q in test_queries:
    print(f"\nQuery: {q}")
    print("── Semantic ──")
    sem = collection.query(query_texts=[q], n_results=2)
    for title in [m["title"] for m in sem["metadatas"][0]]:
        print(f"  {title}")
    print("── Keyword ──")
    kw = keyword_search(q, documents, top_n=2)
    for score, idx, doc in kw:
        print(f"  [{score} matches] {data[idx]['title']}")