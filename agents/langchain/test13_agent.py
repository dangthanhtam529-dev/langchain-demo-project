"""
test13_agent.py - 演示模型使用多个工具
展示 LangChain Agent 如何调用多个工具完成任务
"""

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langchain.tools import tool
from dotenv import load_dotenv
import os

load_dotenv()


# ============================================
# 1. 定义多个工具
# ============================================

@tool
def calculator(expression: str) -> str:
    """
    执行数学计算。
    参数 expression 是数学表达式，例如 "2 + 3"、"100 / 5"、"15 * 3"
    """
    try:
        # 安全计算（只允许基本运算）
        result = eval(expression, {"__builtins__": {}}, {})
        return f"计算结果: {result}"
    except Exception as e:
        return f"计算错误: {e}"


@tool
def get_weather(city: str) -> str:
    """
    查询指定城市的天气。
    参数 city 是城市名称，例如 "北京"、"上海"、"深圳"
    """
    weather_data = {
        "北京": "晴天，气温 25°C，适合出门",
        "上海": "多云，气温 22°C，建议带伞",
        "深圳": "小雨，气温 20°C，注意防滑",
        "广州": "晴天，气温 28°C，注意防晒",
        "成都": "阴天，气温 18°C，适合逛街",
    }
    return weather_data.get(city, f"暂无 {city} 的天气数据")


@tool
def get_current_time() -> str:
    """
    获取当前时间。
    返回格式化的当前时间字符串。
    """
    from datetime import datetime
    now = datetime.now()
    return f"当前时间: {now.strftime('%Y年%m月%d日 %H:%M:%S')}"


@tool
def convert_currency(amount: float, from_currency: str, to_currency: str) -> str:
    """
    货币汇率转换。
    参数:
        amount: 金额
        from_currency: 原货币（如 "USD", "CNY", "EUR"）
        to_currency: 目标货币（如 "USD", "CNY", "EUR"）
    """
    # 模拟汇率数据
    rates = {
        "USD_CNY": 7.2,
        "CNY_USD": 0.14,
        "EUR_CNY": 7.8,
        "CNY_EUR": 0.13,
        "USD_EUR": 0.92,
        "EUR_USD": 1.09,
    }
    key = f"{from_currency.upper()}_{to_currency.upper()}"
    rate = rates.get(key)
    if rate:
        result = amount * rate
        return f"{amount} {from_currency} = {result:.2f} {to_currency} (汇率: {rate})"
    else:
        return f"暂不支持 {from_currency} 到 {to_currency} 的转换"


# ============================================
# 2. 初始化模型
# ============================================

model = init_chat_model(
    "glm-4.7",
    model_provider="openai",
    base_url="https://open.bigmodel.cn/api/paas/v4",
    api_key=os.getenv("ZHIPUAI_API_KEY"),
)


# ============================================
# 3. 创建 Agent（绑定多个工具）
# ============================================

agent = create_agent(
    model=model,
    tools=[calculator, get_weather, get_current_time, convert_currency],
    system_prompt="""你是一个多功能助手，可以帮助用户：
- 进行数学计算（使用 calculator 工具）
- 查询天气信息（使用 get_weather 工具）
- 获取当前时间（使用 get_current_time 工具）
- 转换货币汇率（使用 convert_currency 工具）

请根据用户的问题，选择合适的工具来回答。回答要简洁友好。"""
)


# ============================================
# 4. 测试多个工具调用
# ============================================

test_questions = [
    "帮我计算一下 15 乘以 23 等于多少？",
    "北京今天天气怎么样？",
    "现在几点了？",
    "100美元能换多少人民币？",
    "我今天心情不错，你能帮我算一下 365 除以 7 吗？",
]

print("=" * 60)
print("多工具 Agent 演示")
print("=" * 60)

for i, question in enumerate(test_questions, 1):
    print(f"\n{'=' * 60}")
    print(f"问题 {i}: {question}")
    print(f"{'=' * 60}")

    try:
        result = agent.invoke({"messages": [HumanMessage(content=question)]})
        print(f"回答: {result['messages'][-1].content}")
    except Exception as e:
        print(f"错误: {e}")

print("\n" + "=" * 60)
print("演示完成！")
print("=" * 60)
