# 动态提示词中注入上下文
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from langchain.tools import tool
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent

from langchain.agents.middleware import ModelRequest, dynamic_prompt

from dotenv import load_dotenv
import os



load_dotenv() 

model = init_chat_model(
    model="MiniMax-M2.7",
    model_provider="openai",
    base_url="https://api.minimaxi.com/v1",
    api_key=os.getenv("MINIMAX_API_KEY")  
)

@dynamic_prompt
def prompt_with_user_info(request: ModelRequest) -> str:
    """在提示词中注入用户信息"""
    ctx = request.runtime.context
    user_name = ctx.user_name if ctx else "用户"
    user_plan = ctx.user_plan if ctx else "免费版"

    plan_features = {
        "免费版": "每天 5 次查询",
        "专业版": "每天 100 次查询，支持高级功能",
        "企业版": "无限次查询，优先响应",
    }

    return f"""
你是一个客户服务助手。

当前用户信息：
- 姓名：{user_name}
- 套餐：{user_plan}
- 套餐权益：{plan_features.get(user_plan, "未知")}

请根据用户的套餐信息回答关于使用限额的问题。
如果用户询问升级，介绍更高级套餐的优势。
"""

from pydantic import BaseModel

class UserContext(BaseModel):
    user_name: str
    user_plan: str

agent = create_agent(
    model=model,
    tools=[],
    middleware=[prompt_with_user_info],
    context_schema=UserContext
)
for chunk in agent.stream(
    {"messages": [HumanMessage(content="帮我看我的套餐权益")]},
    context={"user_name": "张三", "user_plan": "专业版"}
):
    if "model" in chunk:
        for msg in chunk["model"]["messages"]:
            if hasattr(msg, "content") and msg.content:
                print(msg.content, end="", flush=True)
