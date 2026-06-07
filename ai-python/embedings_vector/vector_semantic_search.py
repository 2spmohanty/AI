import asyncio

async def get_embeddings(text):
    from clients import openai_client, EMBEDDING_MODEL
    embedding_object = await openai_client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text
    )
    return embedding_object.data[0].embedding


async def search(user_text: str) -> list:
    from clients import supabase_client
    try:
        embedding_vector = await get_embeddings(user_text)

        response =  supabase_client.rpc("match_documents", {"query_embedding": embedding_vector,
                                                              "match_threshold": 0.3,
                                                              "match_count": 2}).execute()
        print(response.data)

    except Exception as e:
        print(e)


user_query = "Jammin' in the Big Easy"

if __name__ == "__main__":
    asyncio.run(search(user_query))