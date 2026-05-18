from langchain_core.runnables import RunnableConfig
from langchain.agents.middleware import before_model
from langchain.messages import RemoveMessage
from langgraph.graph.message import REMOVE_ALL_MESSAGES
from langchain.agents import create_agent, AgentState
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langchain_ollama import ChatOllama 

import os 
from langgraph.runtime import Runtime
from typing import Any
from dotenv import load_dotenv
load_dotenv()  # 载入环境变量 

model = ChatOllama(model="qwen3.5:0.8b", temperature=0.5, reasoning=False)


@before_model
def trim_by_tokens(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    """
    按 Token 数裁剪消息。
    保留最多 4000 个 token 的消息历史。
    """
    messages = state["messages"]

    # 估算 token 数（粗略估算：英文每个单词约 1.3 token）
    total_tokens = 0
    max_tokens = 4000
    keep_messages = []

    # 从最新消息开始保留
    for msg in reversed(messages):
        msg_tokens = len(str(msg.content).split()) * 1.3
        if total_tokens + msg_tokens > max_tokens:
            break
        keep_messages.append(msg)
        total_tokens += msg_tokens

    # 反转回正序
    keep_messages.reverse()

    if len(keep_messages) < len(messages):
        return {
            "messages": [
                RemoveMessage(id=REMOVE_ALL_MESSAGES),
                *keep_messages
            ]
        }
    return None

agent = create_agent(
    model=model,
    middleware=[trim_by_tokens],
    checkpointer=InMemorySaver()
)
config = {"configurable": {"thread_id": "123456"}}
agent.invoke({"messages": [HumanMessage(content="你觉得怎么样才能写出好的测试用例")]}, config=config)
agent.invoke({"messages": [HumanMessage(content="有哪些经典电影值得一看")]}, config=config)
agent.invoke({"messages": [HumanMessage(content="经典港乐有哪些")]}, config=config)
response = agent.invoke({"messages": [HumanMessage(content="你推荐了哪些电影")]}, config=config)
print(response["messages"][-1].content) 
