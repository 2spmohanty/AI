from dotenv import load_dotenv
import os
from huggingface_hub import InferenceClient
from transformers import pipeline


sentimemts = ['Apple beats Q2 earnings estimates by 8 percent', 'Federal Reserve signals further rate hikes ahead',
              'Amazon AWS revenue growth slows for third consecutive quarter',
              'NVIDIA announces record revenue driven by AI chip demand',
              'Banking sector faces increased regulatory scrutiny after collapse']


classification_model ="distilbert/distilbert-base-uncased-finetuned-sst-2-english"

fin_classification_model = "ProsusAI/finbert"

classifier = pipeline("sentiment-analysis", model=fin_classification_model)


for idx,sentimemt in enumerate(sentimemts):
    result = classifier(sentimemt)

    print(f"{idx} - {result}")
