"""
chat.py - 交互式对话 Agent
支持多轮对话，Agent 会记住对话历史
"""

from dotenv import load_dotenv

load_dotenv()

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from config import MAIN_MODEL


# ============================================
# 工具定义
# ============================================
@tool
def calculator(expression: str) -> str:
    """执行数学计算。参数 expression 是数学表达式，例如 "2 + 3 * 4"。"""
    try:
        result = eval(expression)
        return f"计算结果: {result}"
    except Exception as e:
        return f"计算出错: {e}"


@tool
def get_weather(city: str) -> str:
    """查询指定城市的天气情况。"""
    weather_data = {
        "北京": "晴天，气温 25°C",
        "上海": "多云，气温 22°C",
        "深圳": "小雨，气温 20°C",
        "广州": "晴天，气温 28°C",
    }
    return weather_data.get(city, f"暂无 {city} 的天气数据")


# ============================================
# 创建 Agent
# ============================================
checkpointer = InMemorySaver()

agent = create_agent(
    model=init_chat_model(MAIN_MODEL),
    tools=[calculator, get_weather],
    system_prompt=(
        "你是一个多功能助手，可以帮助用户查询天气和进行数学计算。回答要简洁友好。"
    ),
    checkpointer=checkpointer,
)


# ============================================
# 交互循环
# ============================================
if __name__ == "__main__":
    thread_id = "chat_session_1"
    config = {"configurable": {"thread_id": thread_id}}

    print("=" * 50)
    print("LangChain 交互式 Agent")
    print("输入 'quit' 或 'exit' 退出")
    print("=" * 50)

    while True:
        try:
            user_input = input("\n你: ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit"):
            print("再见！")
            break

        print("\nAgent 思考中...", end="", flush=True)

        try:
            result = agent.invoke(
                {"messages": [{"role": "user", "content": user_input}]}, config=config
            )
            print(f"\r{' ' * 20}")  # 清除"思考中"
            print(f"Agent: {result['messages'][-1].content}")
        except Exception as e:
            print(f"\r{' ' * 20}")
            print(f"错误: {e}")
