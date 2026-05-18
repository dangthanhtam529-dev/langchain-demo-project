# 人机协作
from sys import version
from langchain.agents.middleware import HumanInTheLoopMiddleware 

from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.tools import tool 



from langchain_core.messages import HumanMessage
from langchain.chat_models import init_chat_model 
from dotenv import load_dotenv  
import os
load_dotenv()

model = init_chat_model(
    model="MiniMax-M2.7",
    model_provider="openai",
    base_url="https://api.minimaxi.com/v1",
    api_key=os.getenv("MINIMAX_API_KEY")
)

@tool
def send_email_tool(email: str, subject: str, body: str) -> str:
    """发送指定邮箱的邮件"""
    return f"发送邮件到 {email}，主题 {subject}，内容 {body}"

@tool
def delete_data(data: str) -> str:
    """删除指定数据"""
    return f"删除数据: {data}"

agent = create_agent(
    model=model,  
    tools=[delete_data, send_email_tool],
    middleware=[
        HumanInTheLoopMiddleware(
          interrupt_on={
            "delete_data": {
                "allowed_decisions": ["approve", "edit", "reject"]
            },
            "send_email_tool": {
                "allowed_decisions": ["approve", "edit", "reject"]
            }
          }
        )
    ],
    checkpointer=InMemorySaver()
)
config = {"configurable": {"thread_id": "1"}}
response1 = agent.invoke({"messages": "你大概介绍一下电影爱乐之城"}, config,version="v2")  
response2 = agent.invoke({"messages": "删除刚才电影介绍中的多余内容，只保留电影剧情的主要内容"}, config,version="v2")
print(response1.value["messages"][-1].content)
print(response2.value["messages"][-1].content)
  
