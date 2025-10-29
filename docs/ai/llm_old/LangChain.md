简单的基于提示词模板模型调用示例：
```python
from langchain.chat_models.base import init_chat_model
from langchain_core.output_parsers.string import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

PROMPT = """
You are a helpful assistant. 

Role: You're a text analyzer.
Task: extract the most important keywords/phrases of a given piece of text content.
Requirements:
- Summarize the text content, and give top 4 important keywords/phrases.
- The keywords MUST be in language of the given piece of text content.
- The keywords are delimited by ENGLISH COMMA.
- Keywords ONLY in output.

User input:{user_input}
"""

prompt = ChatPromptTemplate.from_template(PROMPT)

llm = init_chat_model(
    model="qwen3:30b-a3b-nothinking",
    model_provider="openai",
    base_url=os.environ.get("OPENAI_BASE_URL"),
    api_key=os.environ.get("OPENAI_API_KEY"),
    temperature=1e-8,
    max_tokens=1024,
)
client = prompt | llm | StrOutputParser()
response = await model.invoke({"user_input": "请解释一下机器学习的基本概念"})
print(response)
```

了解 langchain 的提示词模板配置：
```yaml
messages:
  - role: system
    content: |-
      Role: You're a text analyzer.
      Task: extract the most important keywords/phrases of a given piece of text content.
      Requirements:
      - Summarize the text content, and give top 4 important keywords/phrases.
      - The keywords MUST be in language of the given piece of text content.
      - The keywords are delimited by ENGLISH COMMA.
      - Keywords ONLY in output.
  - role: user
    content: |-
      {user_input}
```

有了以上配置文件后可以通过 `ChatPromptTemplate.model_validate` 函数创建 `ChatPromptTemplate` 对象。
```python
import yaml
from pathlib import Path
from langchain.prompts import ChatPromptTemplate

data = yaml.safe_load(Path("prompt.yaml").read_text(encoding="utf-8"))
prompt = ChatPromptTemplate.model_validate(data)
```

