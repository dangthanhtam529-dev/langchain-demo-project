"""
test10_agent.py - 使用 LangChain Agent 框架处理工具调用
这种方式会自动处理工具调用的复杂逻辑，比手动调用更简单可靠
"""

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
import os
from dotenv import load_dotenv
from langchain.tools import tool

load_dotenv()


@tool
def hello() -> str:
    """当用户输入你好时，返回Hello, World!"""
    return "Hello, World!"


model = init_chat_model(
    model="MiniMax-M2.7",
    model_provider="openai",
    base_url="https://api.minimaxi.com/v1",
    api_key=os.getenv("MINIMAX_API_KEY"),
    timeout=120,
    max_retries=3
)

# 使用 LangChain 的 Agent 框架
# create_agent 会自动处理工具调用的复杂逻辑
agent = create_agent(
    model=model,
    tools=[hello],
    system_prompt="你是一个友好的助手。当用户说'你好'时，使用 hello 工具回应。"
)

# 方式1：使用 invoke（单轮对话）
result = agent.invoke({"messages": [HumanMessage(content="你好")]})
print("方式1 - invoke 结果:")
print(result["messages"][-1].content)
print("-" * 50)

# 方式2：流式输出（实时看到思考过程）
# print("\n方式2 - stream 结果:")
# for chunk in agent.stream({"messages": [HumanMessage(content="你好")]}):
#     if "messages" in chunk:
#         for msg in chunk["messages"]:
#             if hasattr(msg, "content") and msg.content:
#                 print(f"{msg.__class__.__name__}: {msg.content}")
