# pyright: basic

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain.chat_models.base import init_chat_model
from langchain_community.retrievers.bm25 import BM25Retriever
from langchain_core.documents import Document
from langchain_core.output_parsers.string import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 载入目录下的 .env 环境配置
load_dotenv()

# 在 .env 文件中配置 OPENAI_API_BASE、OPENAI_API_KEY 环境变量,例如:
# OPENAI_API_BASE=http://localhost:11434/v1
# OPENAI_API_KEY=my-openai-apikey
EMBEDDING_MODEL = OpenAIEmbeddings(model="emb@bge-m3", check_embedding_ctx_length=False)

# 在这里改变用户输入的问题
# USER_INPUT = "什么是 ExecuTorch?"
# USER_INPUT = "小米汽车的创始人是谁？"
USER_INPUT = "举例说明 ExecuTorch 的常见问题有哪些？"

# -----------------------------------------
# 1. 数据处理:读取知识文档,初始化向量数据库
# -----------------------------------------

docs = []
for file in Path("data", "raw").glob("*"):
    if not file.is_file():
        continue
    content = file.read_text(encoding="utf-8")
    docs.append(Document(page_content=content, metadata={"source": file.name}))

# 实际项目中通常搭配 FAISS/Milvus 方案,此处示例采用适合小规模数据测试的 InMemoryVectorStore
doc_index = InMemoryVectorStore.from_documents(
    [Document(page_content=d.metadata["source"]) for d in docs], EMBEDDING_MODEL
)

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,  # 每块约 500 字符
    chunk_overlap=50,  # 块之间重叠 50 字符,避免资料割裂
)
splits = splitter.split_documents(docs)

chunk_index = InMemoryVectorStore.from_documents(splits, EMBEDDING_MODEL)

# 实际项目中 BM25 检索通常搭配 Elasticsearch 方案,此处示例采用纯算法实现
chunk_bm25_retriever = BM25Retriever.from_documents(splits, k=20)

# -----------------------------------------
# 2. 文档级检索:先找“最可能相关的文档”
# -----------------------------------------

print("\n=== 第一阶段：文档级检索 ===")

doc_result = doc_index.similarity_search(query=USER_INPUT, k=2)
candidate_docs = [d.page_content for d in doc_result]

print("候选文档:", candidate_docs)

# 3. 文档内部 chunk 检索,只在选中的文档内部做:BM25+向量检索 -> rrf -> 精排 (Cross-Encoder Reranker)

print("\n=== 第二阶段：文档内 chunk 检索 ===")

chunk_result = [
    d.page_content
    for d in chunk_index.similarity_search(query=USER_INPUT, k=20)
    if d.metadata["source"] in candidate_docs
]
bm25_chunk_result = [
    d.page_content
    for d in chunk_bm25_retriever.invoke(USER_INPUT)
    if d.metadata["source"] in candidate_docs
]


# rrf 融合 BM25 和向量检索的结果,得到一个更优的排序
def rrf(
    documnents: list[list[str]], k: int = 60, limit: int | None = None
) -> list[tuple[str, float]]:
    """Reciprocal Rank Fusion (RRF)"""
    from collections import defaultdict

    scores = defaultdict(float)
    for ranked in documnents:
        for rank, doc_id in enumerate(ranked, start=1):
            scores[doc_id] += 1.0 / (k + rank)
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return ranked[:limit] if limit else ranked


rrf_ranked_chunks = rrf([chunk_result, bm25_chunk_result], limit=10)

# 精排
...
ranked_chunks = [t for t, _ in rrf_ranked_chunks]

print(f"检索到 {len(ranked_chunks)} 个相关文档片段")

# -----------------------------------------
# 4. LLM 推理层
# -----------------------------------------

MESSAGE = """
你是企业知识库助手。
请仅根据以下资料回答问题。
如果资料不足，请回答“不知道”。

资料：
{context}

问题：
{question}
"""

prompt = ChatPromptTemplate.from_template(MESSAGE)

llm = init_chat_model(
    model="qwen3:30b",
    model_provider="openai",
    base_url=os.environ.get("OPENAI_API_BASE"),
    api_key=os.environ.get("OPENAI_API_KEY"),
    temperature=0.1,
)

chain = prompt | llm | StrOutputParser()
output = chain.invoke(
    {"context": "\n\n---\n\n".join(ranked_chunks), "question": USER_INPUT}
)

print("\n=== LLM 输出 ===")
print(output)

# -----------------------------------------
# 5. 输出示例
# -----------------------------------------

# === 第一阶段：文档级检索 ===
# 候选文档: ['03-frequently-asked-questions.md', '01-getting-started.md']
#
# === 第二阶段：文档内 chunk 检索 ===
# 检索到 10 个相关文档片段
#
# === LLM 输出 ===
# 根据提供的资料，ExecuTorch的常见问题包括：
#
# 1. **What models are supported?**（支持哪些模型？）
#    - 资料中提到：每个hook文档子页面（如useClassification、useLLM等）都包含支持模型部分，列出了在库中几乎无需设置即可运行的模型。
#
# 2. **How can I run my own AI model?**（如何运行自己的AI模型？）
#    - 资料中提到：需要直接访问底层的ExecuTorch Module API，库提供了React hook和TypeScript替代方案，无需深入原生代码即可使用该API。
#
# 3. **Can I run GGUF models using the library?**（能否使用库运行GGUF模型？）
#    - 资料中明确回答：不行，目前ExecuTorch运行时没有可靠方式使用GGUF模型。
#
# 4. **Do you support the old architecture?**（是否支持旧架构？）
#    - 资料中提到：不支持旧架构，目前不计划添加支持。
#
# 5. **Are the models leveraging GPU acceleration?**（模型是否利用GPU加速？）
#    - 资料中提到：iOS上可以使用Core ML（利用CPU、GPU和ANE），但目前没有很多模型导出到Core ML；Android上GPU加速目前有限，大多数模型使用XNNPACK（CPU后端）。
#
# 6. **Can I use React Native ExecuTorch in bare React Native apps?**（能否在bare React Native应用中使用React Native ExecuTorch？）
#    - 资料中回答：可以，从0.8.x版本开始，只需使用bare React Native资源加载器而非Expo加载器。
