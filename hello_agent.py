"""
hello_agent.py - 第一个 LangChain Agent
这是你的入门示例，验证环境搭建是否成功
"""

from dotenv import load_dotenv

load_dotenv()

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.tools import tool
from config import MAIN_MODEL


# ============================================
# 1. 定义工具
# ============================================
@tool
def get_weather(city: str) -> str:
    """查询指定城市的天气情况。参数 city 是城市名称，例如 "北京"、"上海"。"""
    weather_data = {
        "北京": "晴天，气温 25°C，适合出门",
        "上海": "多云，气温 22°C，建议带伞",
        "深圳": "小雨，气温 20°C，注意防滑",
        "广州": "晴天，气温 28°C，注意防晒",
    }
    return weather_data.get(city, f"暂无 {city} 的天气数据")


# ============================================
# 2. 初始化模型
# ============================================
model = init_chat_model(MAIN_MODEL)


# ============================================
# 3. 创建 Agent
# ============================================
agent = create_agent(
    model=model,
    tools=[get_weather],
    system_prompt="你是一个天气助手。使用 get_weather 工具查询天气后，用简洁友好的语言回答用户。",
)


# ============================================
# 4. 运行 Agent
# ============================================
if __name__ == "__main__":
    print("=" * 50)
    print("第一个 LangChain Agent")
    print("=" * 50)

    questions = [
        "北京今天天气怎么样？",
        "上海和深圳哪个天气更好？",
    ]

    for question in questions:
        print(f"\n问题: {question}")
        print("-" * 50)

        result = agent.invoke({"messages": [{"role": "user", "content": question}]})
        print(f"回答: {result['messages'][-1].content}")
        print("=" * 50)
