from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
load_dotenv()

general_model = ChatOllama(model="qwen2.5:7b", temperature=0.3, base_url="http://localhost:11434")
'''
question_model=model = ChatOpenAI(
    model=os.environ["AI_MODEL"],
    temperature=0.8     # Keep low for analytical consistency
)
'''

question_model = ChatOpenAI(
    model=os.environ["AI_MODEL"],
    temperature=0.8  # Keep low for analytical consistency
)

eval_model = ChatOpenAI(
    model=os.environ["AI_JUDGE_MODEL"],
    temperature=0.1  # Keep low for analytical consistency
)