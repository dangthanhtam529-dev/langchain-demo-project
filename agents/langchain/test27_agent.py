# 用小模型做意图分类，路由到不同处理节点
from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage

model = ChatOllama(model="qwen3.5:0.8b", temperature=0.5, reasoning=False)

agent = create_agent(
    model=model,
    system_prompt=f"""
    从用户输入中提取信息，分析用户意图，从以下选项中选择一个：
    - translation: 翻译需求
    - coding: 代码相关问题
    - chat: 日常聊天
    - search: 需要搜索信息
    - complex: 需要深度思考
    
    只返回选项名称，不要解释。
    """
)
response = agent.invoke({"messages": [HumanMessage(content="帮我设计一个分布式系统架构")]})
print(response["messages"][-1].content) 


