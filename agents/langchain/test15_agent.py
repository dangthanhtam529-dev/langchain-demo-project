"""
test15_agent.py - 使用自定义中间件实现动态模型选择
通过 @wrap_model_call 装饰器，在每次模型调用前根据上下文动态切换模型
"""

from collections.abc import Callable

from langchain.agents import create_agent
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langchain.tools import tool
from dotenv import load_dotenv
import os

load_dotenv()


# ============================================
# 1. 初始化多个模型
# ============================================

# 快速模型：处理简单问题（便宜、快）
simple_model = init_chat_model(
    "glm-4-flash",
    model_provider="openai",
    base_url="https://open.bigmodel.cn/api/paas/v4",
    api_key=os.getenv("ZHIPUAI_API_KEY"),
)

# 主模型：处理复杂问题（强大、准确）
complex_model = init_chat_model(
    "glm-4.7",
    model_provider="openai",
    base_url="https://open.bigmodel.cn/api/paas/v4",
    api_key=os.getenv("ZHIPUAI_API_KEY"),
)


# ============================================
# 2. 定义工具
# ============================================

@tool
def calculator(expression: str) -> str:
    """执行数学计算。参数 expression 是数学表达式，如 '2 + 3'"""
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return f"计算结果: {result}"
    except Exception as e:
        return f"计算错误: {e}"


@tool
def get_weather(city: str) -> str:
    """查询城市天气。参数 city 是城市名称"""
    weather_data = {
        "北京": "晴天，25°C",
        "上海": "多云，22°C",
        "深圳": "小雨，20°C",
    }
    return weather_data.get(city, f"暂无 {city} 的天气数据")


# ============================================
# 3. 创建动态模型中间件
# ============================================

@wrap_model_call
def dynamic_model_selector(
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse],
) -> ModelResponse:
    """
    根据用户输入动态选择模型：
    - 简单问题（打招呼、天气）→ 使用快速模型
    - 复杂问题（计算、分析）→ 使用主模型
    """
    # 获取用户最后一条消息
    last_message = request.messages[-1]
    user_input = last_message.content if hasattr(last_message, "content") else str(last_message)

    # 简单问题关键词
    simple_keywords = ["你好", "谢谢", "再见", "天气", "在吗", "早上好", "晚上好"]

    # 判断是否使用快速模型
    use_simple = any(keyword in user_input for keyword in simple_keywords)

    if use_simple:
        print(f"🚀 [动态模型] 检测到简单问题，使用快速模型 (glm-4-flash)")
        selected_model = simple_model
    else:
        print(f"🧠 [动态模型] 检测到复杂问题，使用主模型 (glm-4.7)")
        selected_model = complex_model

    # 使用选中的模型处理请求
    return handler(request.override(model=selected_model))


# ============================================
# 4. 创建 Agent（绑定中间件）
# ============================================

agent = create_agent(
    model=complex_model,  # 默认模型（会被中间件覆盖）
    tools=[calculator, get_weather],
    middleware=[dynamic_model_selector],
    system_prompt="""你是一个智能助手，可以帮助用户：
- 进行数学计算（使用 calculator 工具）
- 查询天气信息（使用 get_weather 工具）
- 回答一般问题

请根据用户的问题选择合适的工具或直接回答。"""
)


# ============================================
# 5. 测试
# ============================================

if __name__ == "__main__":
    test_inputs = [
        "帮我计算 123 乘以 456 等于多少？",
        "你觉得人工智能的未来会怎样？请详细分析",
    ]

    print("=" * 70)
    print("动态模型中间件演示")
    print("=" * 70)

    for i, user_input in enumerate(test_inputs, 1):
        print(f"\n{'=' * 70}")
        print(f"问题 {i}: {user_input}")
        print(f"{'=' * 70}")

        try:
            result = agent.invoke({"messages": [HumanMessage(content=user_input)]})
            print(f"\n回答: {result['messages'][-1].content}")
        except Exception as e:
            print(f"❌ 错误: {e}")

    print("\n" + "=" * 70)
    print("演示完成！")
    print("=" * 70)
