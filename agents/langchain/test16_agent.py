"""
test16_agent.py - 系统提示词（System Prompt）的多种使用方式
演示在 LangChain 中设置系统提示词的不同方法
"""

from langchain.agents import create_agent
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
def get_time() -> str:
    """获取当前时间"""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


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
# 方式 1：通过 create_agent 的 system_prompt 参数
# ============================================

agent1 = create_agent(
    model=model,
    tools=[get_time],
    system_prompt="你是一个幽默的助手，回答问题时总是用轻松的语气。"
)


# ============================================
# 方式 2：使用 SystemMessage 对象
# ============================================

agent2 = create_agent(
    model=model,
    tools=[get_time],
    system_prompt=SystemMessage(content="你是一个严谨的助手，回答问题时总是用专业的术语。")
)


# ============================================
# 方式 3：在消息列表中手动添加 SystemMessage
# ============================================

def chat_with_system_prompt(user_input: str, system_content: str):
    """手动在消息列表中添加系统提示词"""
    messages = [
        SystemMessage(content=system_content),
        HumanMessage(content=user_input)
    ]
    result = model.invoke(messages)
    return result.content


# ============================================
# 方式 4：动态修改系统提示词（每次调用都不同）
# ============================================

def chat_with_dynamic_prompt(user_input: str, style: str):
    """根据参数动态生成系统提示词"""
    styles = {
        "poet": "你是一个诗人，回答问题时总是用优美的诗句。",
        "coder": "你是一个程序员，回答问题时总是用代码示例。",
        "teacher": "你是一个老师，回答问题时总是耐心详细。",
    }
    
    system_content = styles.get(style, "你是一个 helpful 的助手。")
    messages = [
        SystemMessage(content=system_content),
        HumanMessage(content=user_input)
    ]
    result = model.invoke(messages)
    return result.content


# ============================================
# 测试
# ============================================

if __name__ == "__main__":
    print("=" * 70)
    print("系统提示词使用方式演示")
    print("=" * 70)

    # 测试方式 1
    print("\n【方式 1】通过 create_agent 的 system_prompt 参数")
    print("-" * 70)
    result = agent1.invoke({"messages": [HumanMessage(content="今天怎么样？")]})
    print(f"回答: {result['messages'][-1].content}")

    # 测试方式 2
    print("\n【方式 2】使用 SystemMessage 对象")
    print("-" * 70)
    result = agent2.invoke({"messages": [HumanMessage(content="今天怎么样？")]})
    print(f"回答: {result['messages'][-1].content}")

    # 测试方式 3
    print("\n【方式 3】在消息列表中手动添加 SystemMessage")
    print("-" * 70)
    response = chat_with_system_prompt(
        "今天怎么样？",
        "你是一个乐观的助手，回答问题时总是充满正能量。"
    )
    print(f"回答: {response}")

    # 测试方式 4
    print("\n【方式 4】动态修改系统提示词")
    print("-" * 70)
    
    for style in ["poet", "coder", "teacher"]:
        print(f"\n风格: {style}")
        response = chat_with_dynamic_prompt("请解释一下什么是时间", style)
        print(f"回答: {response[:100]}...")

    print("\n" + "=" * 70)
    print("演示完成！")
    print("=" * 70)
