import base64
import os
import requests
from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat.chat_completion import ChatCompletion

load_dotenv()


client = OpenAI(
    api_key=os.environ.get("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)


# Helper function to encode images to base64
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


img_url = "http://images.cocodataset.org/val2017/000000039769.jpg"


# 模拟发送本地图片
os.makedirs("tmp", exist_ok=True)
with open("tmp/image.jpg", "wb") as f:
    f.write(requests.get(img_url).content)


base64_file = encode_image("tmp/image.jpg")


response: ChatCompletion = client.chat.completions.create(
    model="gemini-3.1-flash-lite-preview",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "解释图片"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_file}"  # or data:application/pdf;base64,{base64_file}
                    },
                    #
                    # 云端图片直接填写 URL 地址
                    # "image_url": {
                    #     "url": img_url,
                    # },
                },
            ],
        },
    ],
    temperature=0.1,
)

print("ai:", response.choices[0].message.content)
