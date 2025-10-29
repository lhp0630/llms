import os
from dotenv import load_dotenv
from google.generativeai import GenerationConfig, GenerativeModel, configure

load_dotenv()

configure(api_key=os.environ["GEMINI_API_KEY"])
model = GenerativeModel("gemini-3-flash-preview", system_instruction="你是python专家")
config = GenerationConfig(candidate_count=1, max_output_tokens=1024, temperature=0.0)

session = model.start_chat()

response = session.send_message("什么是python", generation_config=config)
print("\nai:", response.text)

response = session.send_message("写一个fib函数", generation_config=config)
print("\nai:", response.text)

print("\n", len(session.history))
