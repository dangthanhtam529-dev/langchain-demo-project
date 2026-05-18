"""
test17_agent.py - 系统提示词的高级用法
展示动态系统提示词、中间件修改提示词等高级技巧
"""

from collections.abc import Callable

from langchain.agents import create_agent
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.tools import tool
from dotenv import load_dotenv
import os

load_dotenv()


# ============================================
# 定义工具
# ============================================

@tool
def calculator(expression: str) -> str:
    """执行数学计算"""
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return f"计算结果: {result}"
    except Exception as e:
        return f"计算错误: {e}"


# ============================================
# 初始化模型
# ============================================

model = init_chat_model(
     model="MiniMax-M2.7",
    model_provider="openai",
    base_url="https://api.minimaxi.com/v1",
    api_key=os.getenv("MINIMAX_API_KEY")
)


# ============================================
# 方式 1：固定系统提示词（最简单）
# ============================================

def demo_fixed_prompt():
    """固定系统提示词"""
    agent = create_agent(
        model=model,
        tools=[calculator],
        system_prompt="你是一个专业的数学老师，回答简洁明了。"
    )
    result = agent.invoke({"messages": [HumanMessage(content="2+2等于几？")]})
    print("【方式 1】固定系统提示词")
    print(f"回答: {result['messages'][-1].content}")


# ============================================
# 方式 2：动态系统提示词（根据用户输入切换）
# ============================================

def demo_dynamic_prompt():
    """根据用户输入动态选择系统提示词"""
    prompts = {
        "math": "你是一个数学专家，擅长解答数学问题。",
        "poetry": "你是一个诗人，回答问题时总是用优美的诗句。",
        "coding": "你是一个程序员，回答问题时总是用代码示例。",
    }

    user_input = "请解释一下什么是循环"

    for style, prompt in prompts.items():
        messages = [
            SystemMessage(content=prompt),
            HumanMessage(content=user_input)
        ]
        result = model.invoke(messages)
        print(f"\n【方式 2】风格: {style}")
        print(f"回答: {result.content[:80]}...")


# ============================================
# 方式 3：使用中间件动态修改系统提示词
# ============================================

@wrap_model_call
def dynamic_prompt_middleware(
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse],
) -> ModelResponse:
    """中间件：根据对话轮数动态修改系统提示词"""
    message_count = len(request.messages)

    # 获取原始系统提示词
    original_prompt = request.system_message.content

    # 根据对话长度添加不同的指令
    if message_count > 4:
        extra_instruction = "\n\n注意：这是多轮对话，请保持回答的一致性。"
    else:
        extra_instruction = "\n\n注意：这是初次对话，请详细介绍。"

    # 修改系统提示词
    new_content = original_prompt + extra_instruction
    new_system_message = SystemMessage(content=new_content)

    return handler(request.override(system_message=new_system_message))


def demo_middleware_prompt():
    """使用中间件动态修改系统提示词"""
    agent = create_agent(
        model=model,
        tools=[calculator],
        middleware=[dynamic_prompt_middleware],
        system_prompt="你是一个 helpful 的助手。"
    )
    result = agent.invoke({"messages": [HumanMessage(content="你好")]})
    print("【方式 3】中间件修改系统提示词")
    print(f"回答: {result['messages'][-1].content}")


# ============================================
# 方式 4：多轮对话中的系统提示词
# ============================================

def demo_multi_turn():
    """多轮对话中保持系统提示词"""
    system_prompt = "你是一个翻译助手，将用户输入翻译成英文。"

    conversation = [
        SystemMessage(content=system_prompt),
        HumanMessage(content="你好"),
    ]

    # 第一轮
    result = model.invoke(conversation)
    print("【方式 4】多轮对话")
    print(f"第一轮回答: {result.content}")

    # 添加助手回复到对话历史
    conversation.append(result)
    conversation.append(HumanMessage(content="谢谢"))

    # 第二轮
    result = model.invoke(conversation)
    print(f"第二轮回答: {result.content}")


# ============================================
# 方式 5：条件性系统提示词（根据时间/场景）
# ============================================

def demo_conditional_prompt():
    """根据条件（如时间）选择不同的系统提示词"""
    from datetime import datetime

    hour = datetime.now().hour

    if hour < 12:
        prompt = "现在是早上，你的回答应该充满活力和希望。"
    elif hour < 18:
        prompt = "现在是下午，你的回答应该专业且高效。"
    else:
        prompt = "现在是晚上，你的回答应该温和且放松。"

    messages = [
        SystemMessage(content=prompt),
        HumanMessage(content="今天过得怎么样？")
    ]
    result = model.invoke(messages)
    print("【方式 5】条件性系统提示词")
    print(f"当前时间: {hour}点")
    print(f"回答: {result.content}")


# ============================================
# 测试
# ============================================

if __name__ == "__main__":
    print("=" * 70)
    print("系统提示词高级用法演示")
    print("=" * 70)

    demo_fixed_prompt()
    demo_dynamic_prompt()
    demo_middleware_prompt()
    demo_multi_turn()
    demo_conditional_prompt()

    print("\n" + "=" * 70)
    print("演示完成！")
    print("=" * 70)
