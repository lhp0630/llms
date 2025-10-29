import os
from typing import Any, Literal

from dotenv import load_dotenv
from langchain.chat_models.base import init_chat_model
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSequence
from pydantic import BaseModel

load_dotenv()


class AnalysisResult(BaseModel):
    sentiment: Literal["positive", "negative", "neutral"]
    confidence: float
    keywords: list[str]
    summary: str


output_parser = PydanticOutputParser(pydantic_object=AnalysisResult)


# 创建一个提示词模板，其中包括一个系统消息用于描述ai的行为，以及一个用户消息，用于向ai提问
chat_prompt_template = {
    "template_format": "jinja2",
    "messages": [
        {
            "role": "system",
            "content": "You are a helpful assistant.",
        },
        {
            "role": "human",
            "content": """
                分析以下文本的情感并提取关键信息：
        
                文本：{{text}}
                
                请以JSON格式返回结果，包含以下字段：
                - sentiment: 情感分类（positive/negative/neutral）
                - confidence: 置信度（0-1之间的小数）
                - keywords: 关键词列表
                - summary: 摘要（不超过50字）
			""",
        },
    ],
}
prompt = ChatPromptTemplate.model_validate(chat_prompt_template)


async def main():
    # 使用 langchain 封装的函数初始化模型对象
    llm: Any = init_chat_model(
        model="qwen3:30b-a3b-nothinking",
        model_provider="openai",
        base_url=os.environ.get("OPENAI_BASE_URL"),
        api_key=os.environ.get("OPENAI_API_KEY"),
        temperature=1e-8,
        max_tokens=1024,
    )

    # langchain 支持链式调用，这里实际上是依次执行 invoke 函数，并将执行结果传给下一个 invoke 函数
    # 将 prompt 链接到模型对象上，接着使用模型对象进行推理，获取模型输出，最后将模型输出转换成字符串
    model: RunnableSequence[dict[str, str], AnalysisResult] = (
        prompt | llm | output_parser
    )

    # 调用模型，获取链式调用的结果
    response = await model.ainvoke(
        {
            "text": "Python的静态类型检查工具Pyright非常强大，与LangChain结合使用可以大幅提升开发效率！"
        }
    )
    print(response.model_dump())


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
