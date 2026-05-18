from langchain.agents import AgentState, create_agent
from langchain.tools import tool, ToolRuntime
from langchain_core.messages import HumanMessage
from langchain.chat_models import init_chat_model 
from dotenv import load_dotenv  
import os
load_dotenv()
from langchain.chat_models import init_chat_model

model = init_chat_model(
    model="MiniMax-M2.7",
    model_provider="openai",
    base_url="https://api.minimaxi.com/v1",
    api_key=os.getenv("MINIMAX_API_KEY")
)

class CustomState(AgentState):
    user_name: str
    user_preferences: dict


@tool
def get_user_info(runtime: ToolRuntime[CustomState]) -> str:
    """获取当前用户的信息"""
    user_name = runtime.state.get("user_name", "未知")
    prefs = runtime.state.get("user_preferences", {})

    info = f"用户: {user_name}\n"
    info += f"偏好: {prefs}"
    return info


agent = create_agent(
    model=model,
    tools=[get_user_info],
    state_schema=CustomState
)

# 调用时传入自定义状态
result = agent.invoke({
    "messages": [{"role": "user", "content": "介绍一下我的信息"}],
    "user_name": "小明",
    "user_preferences": {"语言": "中文", "风格": "简洁"}
})
print(result["messages"][-1].content)
