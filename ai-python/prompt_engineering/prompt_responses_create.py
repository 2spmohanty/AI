from openai import OpenAI
from dotenv import load_dotenv
import os
import asyncio
from openai import AsyncOpenAI

load_dotenv()

api_key = os.getenv("AI_KEY")
ai_url = os.getenv("AI_URL")
ai_model = os.getenv("AI_MODEL")

openai = AsyncOpenAI(api_key=api_key, base_url=ai_url)

print("Established connection. Requesting story...")

chatMessage = [{
    "role": "system",
    "content": "You are the Google Search for Budget Friendly."
}]


async def chat(user_message):
    chatMessage.append({
        "role": "user",
        "content": user_message
    })
    response = await openai.responses.create(model=ai_model,
                                             input=chatMessage,
                                             tools=[{"type": "web_search"}],
                                             )
    result = response.output_text
    print("#"*50)
    print(response.output)
    print("#" * 50)
    chatMessage.append({
        "role": "assistant",
        "content": result
    })

    print("*" * 50)
    print(result)
    print("*"*50)

    print("\n"*4)


async def main():
    await chat("Suggest me good coffee machine to buy in Bengaluru, India.")
    await chat("Suggest Matching coffee beans, that will go well with this.")
    await chat("Suggest Cost effective options for buying coffee machine and beans.")


asyncio.run(main())
