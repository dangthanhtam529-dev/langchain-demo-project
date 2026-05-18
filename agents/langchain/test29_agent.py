from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware
from langgraph.checkpoint.memory import InMemorySaver
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
from langchain.chat_models import init_chat_model 
from dotenv import load_dotenv  
import os
load_dotenv()

checkpointer = InMemorySaver()

model_1 = init_chat_model(
    model="MiniMax-M2.7",
    model_provider="openai",
    base_url="https://api.minimaxi.com/v1",
    api_key=os.getenv("MINIMAX_API_KEY")
)
model_2 = ChatOllama(model="qwen3.5:0.8b", temperature=0.5, reasoning=False)
agent = create_agent(
    model=model_1,  
    tools=[],
    middleware=[
        SummarizationMiddleware(
            model=model_2,  # 用一个小模型来做摘要，节省成本  
            trigger=("tokens", 4000),  # 当消息总 token 超过 4000 时触发
            keep=("messages", 20)      # 保留最近 20 条消息不摘要
        )
    ],
    checkpointer=checkpointer
)

config = {"configurable": {"thread_id": "1"}}

# 长对话
agent.invoke({"messages": "hi, my name is bob"}, config)
agent.invoke({"messages": "write a short poem about cats"}, config)
agent.invoke({"messages": "now do the same but for dogs"}, config)

# Agent 仍然能记住名字，因为早期对话被总结成了摘要
final_response = agent.invoke({"messages": "what's my name?"}, config)
print(final_response["messages"][-1].content)