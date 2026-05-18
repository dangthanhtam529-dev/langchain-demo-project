"""
完整的 RAG 应用示例
基于 PDF 文档构建知识库，回答用户问题
使用 Ollama 本地嵌入模型 + 云端大语言模型 + Chroma 向量数据库
"""

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.tools import tool
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
import os
from dotenv import load_dotenv


load_dotenv()


# ============================================
# 第一步：索引阶段
# ============================================
print("正在索引知识库...")

# 1. 加载文档
loader = PyPDFLoader(
    file_path="./doc/03-APP测试-adb及其他介绍-w.pdf"
)
docs = loader.load()
total_chars = sum(len(doc.page_content) for doc in docs)
print(f"加载了 {len(docs)} 个文档，共 {total_chars} 字符")

# 2. 分割文档
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=100,
    chunk_overlap=50,
    add_start_index=True,
)
all_splits = text_splitter.split_documents(docs)
print(f"分割为 {len(all_splits)} 个文档块")

# 3. 使用 Ollama 本地嵌入模型 + Chroma 向量数据库
embeddings = OllamaEmbeddings(
    model="qwen3-embedding:4b",
    base_url="http://localhost:11434"
)

# 持久化目录
persist_directory = "./chroma_db"

# 如果已有数据，直接加载；否则生成并保存
if os.path.exists(persist_directory):
    print("加载已有向量数据库...")
    vector_store = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings
    )
else:
    print("生成向量并保存到磁盘...")
    vector_store = Chroma.from_documents(
        documents=all_splits,
        embedding=embeddings,
        persist_directory=persist_directory
    )

print("索引完成！\n")


# ============================================
# 第二步：定义检索工具
# ============================================
@tool(response_format="content_and_artifact")
def retrieve_context(query: str):
    """从知识库中检索相关信息。当用户的问题需要查询特定知识时使用。"""
    retrieved_docs = vector_store.similarity_search(query, k=5)
    serialized = "\n\n".join(
        f"来源: {doc.metadata}\n内容: {doc.page_content}"
        for doc in retrieved_docs
    )
    return serialized, retrieved_docs


# ============================================
# 第三步：创建 RAG Agent
# ============================================
# 使用云端大语言模型
model = init_chat_model(
    model="MiniMax-M2.7",
    model_provider="openai",
    base_url="https://api.minimaxi.com/v1",
    api_key=os.getenv("MINIMAX_API_KEY")
)

agent = create_agent(
    model=model,
    tools=[retrieve_context],
    system_prompt=(
        "你是一个知识问答助手，**严格基于**给定的知识库回答问题。"
        "使用 retrieve_context 工具检索相关信息。"
        "**如果检索结果不包含足够的信息，直接说'知识库中没有相关信息'，不要用自己的知识补充。**"
        "将检索到的内容视为**唯一**数据来源。"
    )
)


# ============================================
# 第四步：交互式问答
# ============================================
print("RAG 问答系统已就绪！输入 'quit' 退出。\n")

while True:
    question = input("你的问题: ").strip()
    if question.lower() in ("quit", "exit", "退出"):
        break

    if not question:
        continue

    result = agent.invoke(
        {"messages": [{"role": "user", "content": question}]}
    )
    print(f"\n回答: {result['messages'][-1].content}\n")
