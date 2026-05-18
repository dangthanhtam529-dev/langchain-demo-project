from dotenv import load_dotenv
import os

load_dotenv()


from langchain.agents import create_agent
from langchain.tools import tool
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, AIMessage

# 标准库导入
import requests



@tool
def get_current_weather(location: str) -> str:
    """
    获取指定位置的当前天气
    
    参数:
        location: 城市名称，例如 "北京"、"上海"
    
    返回:
        天气信息的文本描述
    
    工作原理:
        - 调用外部天气 API 获取实时数据
        - 返回格式化的天气信息
    """
    url = f"http://shanhe.kim/api/za/tianqi.php?city={location}"
    response = requests.get(url)
    return response.text



model = init_chat_model(
    "glm-4.7",
    model_provider="openai",
    base_url="https://open.bigmodel.cn/api/paas/v4",
    api_key=os.getenv("ZHIPUAI_API_KEY"),
)



agent = create_agent(
    model=model,
    tools=[get_current_weather],
    system_prompt="你是一个友好的天气助手。当用户询问天气时，使用 get_weather 工具查询后回答。"
)


for step in agent.stream(
    {"messages": [{"role": "user", "content": "北京今天天气怎么样？"}]},
    stream_mode="values",
):
    # 获取最新的一条消息
    latest_message = step["messages"][-1]

    # 根据消息类型打印不同的内容
    if isinstance(latest_message, HumanMessage):
        print(f"\n👤 用户: {latest_message.content}")
    elif isinstance(latest_message, AIMessage):
        # 如果模型调用了工具
        if latest_message.tool_calls:
            for tc in latest_message.tool_calls:
                print(f"🔧 调用工具: {tc['name']}({tc['args']})")
        # 如果模型有文本回复
        elif latest_message.content:
            print(f"🤖 Agent: {latest_message.content}")