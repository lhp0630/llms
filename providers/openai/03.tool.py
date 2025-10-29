import os
from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat.chat_completion import ChatCompletion

load_dotenv()


client = OpenAI(
    api_key=os.environ.get("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)


def fetch_current_weather(city: str, unit="Celsius") -> str:
    return "It's sunny and warm."


# 遵循 Function Calling 规范定义 fetch_current_weather 函数说明
# 模型会根据函数说明，动态的获取所需的实时数据提供给我们的系统
tools = [
    {
        "type": "function",
        "function": {
            "name": "fetch_current_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The city for which to fetch the weather",
                    },
                    "unit": {},
                },
                "required": ["city"],
            },
        },
    }
]


response: ChatCompletion = client.chat.completions.create(
    model="gemini-3-flash-preview",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What the weather like in Paris?"},
    ],
    temperature=0.1,
    tools=tools,
)

# 通过 tool_calls 可以获取到用户问题中提到的城市名称
arguments = response.choices[0].message.tool_calls[0].function.arguments
print(arguments)  # {"city":"Paris"}

# 这种机制大大的提升了系统与模型交互的智能型和实用性
# 允许模型与外部系统进行交互，通过定义工具，从而实现系统可以动态的调用函数，获取实时数据或执行复杂操作
