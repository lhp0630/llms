from dotenv import load_dotenv
from litellm import completion


# os.environ["GEMINI_API_KEY"] = "xxx"
load_dotenv()


response = completion(
    model="gemini/gemini-3-flash-preview",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Please reply ok"},
    ],
)

print("\nai:", response.choices[0].message.content)
