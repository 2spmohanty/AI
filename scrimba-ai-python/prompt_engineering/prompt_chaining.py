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
    "content": "You are a Gift idea suggestion specialist. You need to suggest 5 gift items, based on the user ask and theme."
}]


async def chat(user_message):
    chatMessage.append({
        "role": "user",
        "content": user_message
    })
    response = await openai.chat.completions.create(model=ai_model, messages=chatMessage)
    system_message_obj = response.choices[0].message
    chatMessage.append(system_message_obj)
    print("AI response: {}".format(system_message_obj.content))


async def main():
    await chat("Suggest me some gift for Anshuman.")
    await chat("Anshuman is my childhood friend.")
    await chat("He is a sports person, and likes Badminton and TT but has left the game long back.")

asyncio.run(main())
