from dotenv import load_dotenv
import os
import asyncio
from openai import AsyncOpenAI
import json
from pydantic import BaseModel, ConfigDict
from typing import List, Dict

load_dotenv()

api_key = os.getenv("AI_KEY")
ai_url = os.getenv("AI_URL")
ai_model = os.getenv("AI_MODEL")


class RiskFactors(BaseModel):
    market_risk: str
    regulatory_risk: str
    competition_risk: str



class StockReport(BaseModel):
    quarter: str
    ticker: str
    sentiment: str
    price_target: float
    reasoning: str
    confidence_score: float
    risk_factors: RiskFactors


class Report(BaseModel):

    quarterly_results: List[StockReport]




openai = AsyncOpenAI(api_key=api_key, base_url=ai_url)

print("Established connection. Initiating Workflow...")

system_message = """
"You are a Stock Analyst. We need to predict the stock market for 2 consecutive instance i.e next two fiscal quarters for a company received in user input.
The output should be consensus analyst estimates from any one top source.
Your output should contain fields — ticker, sentiment, price_target, reasoning, confidence_score and risk factors.
"""

chatMessage = [{
    "role": "system",
    "content": system_message
}]




async def search(user_message):
    chatMessage.append({
        "role": "user",
        "content": user_message
    })
    response = await openai.responses.create(model=ai_model,
                                             input=chatMessage,
                                             tools= [{"type" : "web_search_preview"}])
    return response.output_text

stock_formatter = (f"You are a formatting specialist. "
                   f"Your Job is to extract data as returned by tool type web_search_preview.")

async def structure(search_message):
    message = [{"role": "system", "content":  stock_formatter },
               {"role": "user", "content":  search_message }]
    response = await openai.responses.parse(model=ai_model,input=message, text_format=Report)
    return response.output_parsed


async def stock_analysis(user_message):
    search_result = await search(user_message)
    structured_result = await structure(search_result)
    print("Structured result: {}".format(structured_result))


async def stock_analysis_v1(workflow_message,user_message):
    # Combine search and extraction into one single call
    response = await openai.responses.parse(
        model=ai_model,
        input=[
            {"role": "system", "content": workflow_message},
            {"role": "user", "content": user_message}
        ],
        tools=[{"type": "web_search_preview"}],
        text_format=Report  # Native Pydantic support
    )

    # Access the parsed object immediately
    structured_result = response.output_parsed
    print(f"Structured result: {structured_result}")


async def main():
    await stock_analysis("Get me Amazon's stock Analysis.")
    #await stock_analysis_v1(system_message,"Get me Microsoft's stock Analysis.")


asyncio.run(main())
