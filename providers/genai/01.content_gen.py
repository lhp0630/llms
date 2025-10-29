import os
from dotenv import load_dotenv
from google.generativeai import GenerationConfig, GenerativeModel, configure

load_dotenv()

configure(api_key=os.environ["GEMINI_API_KEY"])
model = GenerativeModel("gemini-3-flash-preview", system_instruction="你是llm领域专家")
prompt = """
请解释一下机器学习的基本概念
"""

response = model.generate_content(
    prompt,
    generation_config=GenerationConfig(
        candidate_count=1, max_output_tokens=1024, temperature=0.0
    ),
)
print("\nai:", response.text)
