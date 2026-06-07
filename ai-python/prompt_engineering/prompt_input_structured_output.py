from openai import OpenAI
from dotenv import load_dotenv
import os
import asyncio
from openai import AsyncOpenAI
import json
from pydantic import BaseModel

load_dotenv()

api_key = os.getenv("AI_KEY")
ai_url = os.getenv("AI_URL")
ai_model = os.getenv("AI_MODEL")

openai = AsyncOpenAI(api_key=api_key, base_url=ai_url)

print("Established connection. Requesting story...")

stock_schema = {
    "name": "stock_report",
    "schema": {
        "type": "object",
        "properties": {
            "ticker": {"type": "string"},
            "sentiment": {"type": "string"},
            "price_target": {"type": "number"},
            "reasoning": {"type": "string"},
            "confidence_score": {"type": "number"},

        },
        "required": ["ticker", "sentiment", "price_target", "reasoning", "confidence_score"]
    }
}

class RiskFactors(BaseModel):
    market_risk: str
    regulatory_risk: str
    competition_risk: str



class StockReport(BaseModel):
    ticker: str
    sentiment: str
    price_target: float
    reasoning: str
    confidence_score: float
    risk_factors: RiskFactors



chatMessage = [{
    "role": "system",
    "content": "You are a Stock Analyst. We need to predict the stock market for 3 consecutive instance and gather response for Amazon. "
               "Your output should be a JSON format report, with specific fields — ticker, sentiment, price_target, reasoning, confidence_score. ",

}]


async def board(user_message):
    chatMessage.append({
        "role": "user",
        "content": user_message
    })
    '''
    response = await openai.chat.completions.create(model=ai_model, messages=chatMessage,
                                                    response_format={"type": "json_schema", "json_schema": stock_schema})
    system_message_obj = response.choices[0].message

    report = json.loads(system_message_obj.content)

    print(f"Ticker: {report['ticker']}\nSentiment: {report['sentiment']}\nPrice Target: {report['price_target']}\nReasoning: {report['reasoning']}\nConfidence Score: {report['confidence_score']}")


    '''
    response = await openai.beta.chat.completions.parse(model=ai_model, messages=chatMessage,
                                                    response_format=StockReport)
    system_message_obj = response.choices[0].message
    chatMessage.append(system_message_obj)

    stock_report : StockReport = system_message_obj.parsed
    print(f"Stock Report: {stock_report}")

    print(
        f"Ticker: {stock_report.ticker}\nSentiment: {stock_report.sentiment}\nPrice Target: {stock_report.price_target}\nReasoning: {stock_report.reasoning}\nConfidence Score: {stock_report.confidence_score}")

    print("Risk Analysis: \n")
    risk_factors : RiskFactors = stock_report.risk_factors
    print(f"Market Risk Factors: {risk_factors.market_risk}\nRegulator Risk: {risk_factors.regulatory_risk}\nCompletion Risk: {risk_factors.competition_risk}")

async def main():
    await board("Start Market analysis for 22 May 2026.")


asyncio.run(main())
