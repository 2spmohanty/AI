import asyncio
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.providers.ollama import OllamaProvider
from openai import AsyncOpenAI
import json

# Flattened schema to help Ollama's structured output
class StockReport(BaseModel):
    quarter: str
    ticker: str
    sentiment: str
    price_target: float = Field(description="Numeric price target, not a string")
    reasoning: str
    confidence_score: float = Field(description="0.0 to 1.0")
    market_risk: str
    regulatory_risk: str
    competition_risk: str


class Report(BaseModel):
    quarterly_results: list[StockReport] = Field(
        description="Exactly 2 quarterly reports"
    )

client = AsyncOpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)



system_message = """You are a stock analyst. Return ONLY valid JSON matching this schema exactly.

{
  "quarterly_results": [
    {
      "quarter": "Q1 2025",
      "ticker": "AAPL",
      "sentiment": "bullish|neutral|bearish",
      "price_target": 250.0,
      "confidence_score": 0.75,
      "reasoning": "<explain the key factors driving this outlook>",
      "market_risk": "<describe the primary market risk for this quarter>",
      "regulatory_risk": "risk description",
      "competition_risk": "risk description"
    }
  ]
}

Rules:
1) quarterly_results must have exactly 2 items
2) price_target and confidence_score must be numbers (not strings)
3) Output ONLY JSON, no markdown, no text before/after
4) All fields are required
"""


async def main():
    user_input = "Apple Inc. (AAPL)"

    response = await client.chat.completions.create(
        model="llama3.2",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_input}
        ],
        response_format={"type": "json_object"},
        temperature=0.5
    )
    raw = response.choices[0].message.content
    data = json.loads(raw)
    report = Report.model_validate(data)
    print(report.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(main())