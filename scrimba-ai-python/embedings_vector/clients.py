from openai import AsyncOpenAI
import os
from dotenv import load_dotenv
from supabase import create_client, Client


load_dotenv()

EMBEDDING_MODEL= "text-embedding-ada-002"

openai_client = AsyncOpenAI(
    api_key=os.getenv("AI_KEY")
)

supabase_client: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

