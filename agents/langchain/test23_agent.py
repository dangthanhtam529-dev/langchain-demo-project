# 短期记忆
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage

from langgraph.checkpoint.memory import InMemorySaver
from dotenv import load_dotenv
import os

load_dotenv()
model = init_chat_model(
    model="MiniMax-M2.7",
    model_provider="openai",
    base_url="https://api.minimaxi.com/v1",
    api_key=os.getenv("MINIMAX_API_KEY")
)
agent = create_agent(
    model=model,
    system_prompt="你是一个生活助手助手，根据用户的问题回答问题。回答要专业、客观。",
    checkpointer=InMemorySaver()
)

config = {"configurable": {"thread_id": "123456"}}


response = agent.invoke({"messages": [HumanMessage(content="我是一个喜欢安静的人")]}, config=config)
print(response)

response = agent.invoke({"messages": [HumanMessage(content="你觉得我的性格适合听什么音乐")]}, config=config)
print(response)