# 测试本地小模型的翻译能力
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain_core.messages import SystemMessage, HumanMessage 
from dotenv import load_dotenv  

load_dotenv()
import os 

from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="qwen3.5:0.8b",
    temperature=0.1,
    reasoning=False 
)

agent = create_agent(
    model=llm,
    system_prompt="你是一个翻译助手，根据用户的问题翻译。"
)
response = agent.invoke({"messages": [HumanMessage(content="	Investors are advised to diversify their portfolios to mitigate market volatility risks.是什么意思")]})
print(response["messages"][-1].content) 
