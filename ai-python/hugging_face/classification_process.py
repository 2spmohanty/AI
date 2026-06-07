from huggingface_hub import InferenceClient
from dotenv import load_dotenv
import os
from huggingface_hub import InferenceClient
load_dotenv()


client = InferenceClient(
    provider="hf-inference",
    api_key=os.environ["HF_TOKEN"],
)

input_text = """A cherry blossom is the flower from a Prunus tree, of which there are many different kinds. 
              "Species cherry blossoms are found throughout the world being especially common in regions in the 
              "Northern Hemisphere with temperate climates, including Japan, China, and Korea, as well as Nepal, 
              "India, Pakistan, Iran, and Afghanistan, and several areas across northern Europe.
              "Japan is particularly famous for its cherry blossom due its large number of varieties and the 
              "nationwide celebrations during the blooming season. 
              "As the buds burst open in parks and streets across the country, 
              "people throw picnic and hanami (flower viewing) parties to appreciate the transient 
              "beauty of the flowers and welcome in the warmer weather. 
              "Cherry blossoms in Japanese are known as sakura and it would not be an 
              "exaggeration to say they are a national obsession."""


#result = client.summarization( input_text, model="facebook/bart-large-cnn")

classification_input = ("When i saw you for the first time, my time froze. "
                        "I wish i can capture that moment store it in my showcase never to be used again.")

classification_model ="distilbert/distilbert-base-uncased-finetuned-sst-2-english"

result = client.text_classification(input_text,model=classification_model)

print(result)