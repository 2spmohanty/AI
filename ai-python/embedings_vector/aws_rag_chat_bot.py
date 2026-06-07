import os
import chromadb
from dotenv import load_dotenv
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from openai import AsyncOpenAI
import sys
from collections import defaultdict
import asyncio

load_dotenv()


# Client and Collection Setup
chroma_client = chromadb.PersistentClient(path="./aws_chroma_db")
openai_ef = OpenAIEmbeddingFunction(
    api_key=os.getenv("AI_KEY"),
    model_name="text-embedding-3-small"
)

collection = chroma_client.get_or_create_collection(
    name="aws_architect",
    embedding_function=openai_ef,
    configuration={
        "hnsw": {
            "space": "cosine",
            "ef_construction": 200
        }
    }
)


async def get_rag_result(query):
    # ChromaDB local queries are synchronous; we run them in an executor to prevent blocking
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(
        None,
        lambda: collection.query(
            query_texts=[query],
            include=["documents", "metadatas"],
            n_results=5
        )
    )

    page_dict = defaultdict(list)

    # ChromaDB returns nested lists for batches. Index [0] extracts results for our single query string.
    documents = result.get("documents", [[]])[0]
    metadatas = result.get("metadatas", [[]])[0]

    for document, metadata in zip(documents, metadatas):
        if metadata and 'page' in metadata:
            page_dict[metadata['page']].append(document)

    return dict(page_dict)


system_prompt_template = """You are a Principal AWS Cloud Solutions Architect. Your role is to provide authoritative, professional, and highly actionable architectural guidance based strictly on the provided context.

RESPONSE GUIDELINES:
- Synthesize all relevant pieces of context across the provided pages into a unified, cohesive architectural strategy.
- Adopt the persona of a seasoned professional: use clear engineering terminology, explain the "why" behind your recommendations, and structure your response logically using technical headings and bullet points.
- Reference the relevant source page numbers from the context when making specific factual claims to maintain architectural traceability.

OUTPUT FORMAT:
Your response must strictly follow this structural layout:
### 1. Executive Summary
- Provide a brief, high-level overview of the recommended architectural approach.

### 2. Architectural Recommendation & Best Practices
- Break down the core technical solution using subheadings where appropriate.
- Detail the specific components, configurations, and patterns required.
- Cite the source page numbers in brackets, for example: (Page 4).

### 3. Design Justification & "Why"
- Explain the engineering rationale behind this pattern.
- Detail the operational, security, or performance benefits based on the context.

STRICT RULES:
1. User Question: {query}
2. Context and Knowledge: {context}

Note on Context Format:
The context is provided as a dictionary where keys are page numbers and values are lists of content text from that specific page. For example:
{{
    0: ["AWS S3 Life Cycle Management", "S3 IAM Policies"],
    4: ["Storage Options in cloud", "EBS in AWS", "Ephemeral Volumes"]
}}

3. If you lack sufficient information in the context, do not make up an answer. Instead, say exactly:
'I lack the information for this taste profile and will need more data to recommend confidently.'"""

async_client = AsyncOpenAI(api_key=os.getenv("AI_KEY"))


async def get_architect_response(user_query, retrieved_context):
    final_system_prompt = system_prompt_template.format(
        query=user_query,
        context=retrieved_context
    )

    stream = await async_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": final_system_prompt},
            {"role": "user", "content": user_query}
        ],
        temperature=0.3,
        stream=True
    )

    async for chunk in stream:
        content = chunk.choices[0].delta.content
        if content:
            print(content, end="", flush=True)
    print("\n")


async def chat():
    print("Hi, I am Niko, an AWS Professional Expert. How can I help you today?")

    # Keeps the conversation running until user type 'bye'
    while True:
        try:
            query = input("\nUser > ").strip()
            if not query or query.lower() == "bye":
                print("Goodbye!")
                sys.exit()

            print("\nArchitect is thinking...", flush=True)
            context = await get_rag_result(query)

            print("Response:\n")
            await get_architect_response(query, context)

        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            sys.exit()


if __name__ == "__main__":

    asyncio.run(chat())