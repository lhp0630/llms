import os

from dotenv import load_dotenv
from langchain.chat_models.base import init_chat_model
from langchain_core.output_parsers.string import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()


# 创建一个提示词模板，其中包括一个系统消息用于描述ai的行为，以及一个用户消息，用于向ai提问
prompt_template = {
    "template_format": "jinja2",
    "messages": [
        {
            "role": "system",
            "content": "你是一个友好的聊天机器人",
        },
        {
            "role": "human",
            "content": "{{user_input}}",
        },
    ],
}
prompt = ChatPromptTemplate.model_validate(prompt_template)


async def main():
    # 使用 langchain 封装的函数初始化模型对象
    llm = init_chat_model(
        model="qwen3:30b-a3b-nothinking",
        model_provider="openai",
        base_url=os.environ.get("OPENAI_BASE_URL"),
        api_key=os.environ.get("OPENAI_API_KEY"),
        temperature=1e-8,
        max_tokens=1024,
    )

    # langchain 支持链式调用，这里实际上是依次执行 invoke 函数，并将执行结果传给下一个 invoke 函数
    # 将 prompt 链接到模型对象上，接着使用模型对象进行推理，获取模型输出，最后将模型输出转换成字符串
    model = prompt | llm | StrOutputParser()

    # 调用模型，获取链式调用的结果
    response = await model.ainvoke({"user_input": "请解释一下机器学习的基本概念"})
    print(response)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
