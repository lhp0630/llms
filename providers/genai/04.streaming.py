import os
from dotenv import load_dotenv
from google.generativeai import GenerationConfig, GenerativeModel, configure

load_dotenv()

configure(api_key=os.environ["GEMINI_API_KEY"])
model = GenerativeModel("gemini-3-flash-preview")
prompt = """
这是一次测试请求，写一首短诗
"""

response = model.generate_content(
    prompt,
    stream=True,
    generation_config=GenerationConfig(
        candidate_count=1, max_output_tokens=1024, temperature=0.0
    ),
)

print("\nai:")
for chunk in response:
    print(chunk.text)
