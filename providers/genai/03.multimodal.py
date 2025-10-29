import os
from io import BytesIO
import requests
from dotenv import load_dotenv
from google.generativeai import GenerationConfig, GenerativeModel, configure
from PIL import Image

load_dotenv()

configure(api_key=os.environ["GEMINI_API_KEY"])

model = GenerativeModel("gemini-3.1-flash-lite-preview")

img_url = "http://images.cocodataset.org/val2017/000000039769.jpg"
image = Image.open(BytesIO(requests.get(img_url).content))

response = model.generate_content(
    ["解释图片", image],
    generation_config=GenerationConfig(
        candidate_count=1, max_output_tokens=1024, temperature=0.0
    ),
)

print("\nai:", response.text)
