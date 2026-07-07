from openai import AsyncOpenAI
import asyncio

client = AsyncOpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

print("Established connection. Requesting story...")

chatMessage = [{
    "role": "system",
    "content": "You are the Google Search for Budget Friendly."
}]

ai_model = "llama3.2"

async def chat(user_message):
    chatMessage.append({
        "role": "user",
        "content": user_message
    })
    response = await client.chat.completions.create(model=ai_model,
                                             messages=chatMessage
                                             )
    result = response.choices[0].message.content
    print("#"*50)
    print(response.choices)
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


asyncio.run(main())
