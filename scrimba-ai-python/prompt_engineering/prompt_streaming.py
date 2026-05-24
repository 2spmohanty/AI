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
    "content": "You are a Gift idea suggestion specialist. You need to suggest 3 gift items, based on the user ask and theme."
               "You need to return the answer in JSON array format with three keys 1) name (gift name) 2) reason (Why it works) 3) location_list (An array Where to get it)."
}]


async def chat(user_message):
    chatMessage.append({
        "role": "user",
        "content": user_message
    })
    response = await openai.chat.completions.create(model=ai_model, messages=chatMessage, stream=True)
    #system_message_obj = response.choices[0].message
    #chatMessage.append(system_message_obj)
    full_content = ""

    print("AI response: ",end="", flush=True)
    async for chunk in response:
        content = chunk.choices[0].delta.content
        if content:
            full_content += content
            print(content,end="", flush=True)
    print("\n")
    chatMessage.append({"role": "assistant", "content": full_content})



async def main():
    await chat("Suggest me some gift for Anshuman.")
    await chat("Anshuman is my childhood friend.")

asyncio.run(main())
