# 动态提示词 @dynamic_prompt 中间件 - 实际应用示例
from langchain.agents import create_agent
from langchain.agents.middleware import dynamic_prompt, ModelRequest
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langchain.tools import tool
from dotenv import load_dotenv
import os 

load_dotenv() 

model = init_chat_model(
    model="MiniMax-M2.7",
    model_provider="openai",
    base_url="https://api.minimaxi.com/v1",
    api_key=os.getenv("MINIMAX_API_KEY")  
)

@tool
def calculator(expression: str) -> str:
    """执行数学计算"""
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return f"计算结果: {result}"
    except Exception as e:
        return f"计算错误: {e}"

# ============================================
# 实际应用 1：从用户输入自动推断
# ============================================
@dynamic_prompt
def auto_infer_prompt(request: ModelRequest) -> str:
    """根据用户输入内容自动推断角色"""
    user_input = request.messages[-1].content
    
    # 关键词推断
    if any(kw in user_input for kw in ["代码", "编程", "python", "函数"]):
        return "你是一个程序员，用代码示例回答问题，解释清晰。"
    elif any(kw in user_input for kw in ["数学", "计算", "公式", "等于"]):
        return "你是一个数学老师，详细解释计算过程，步骤清晰。"
    elif any(kw in user_input for kw in ["翻译", "英文", "中文"]):
        return "你是一个翻译助手，提供准确翻译和例句。"
    else:
        return "你是一个通用助手，回答简洁专业。"

# ============================================
# 实际应用 2：模拟从数据库获取用户画像
# ============================================
def get_user_profile(user_id: str) -> dict:
    """模拟从数据库获取用户信息"""
    profiles = {
        "user_1": {"level": "expert", "style": "technical"},
        "user_2": {"level": "beginner", "style": "simple"},
        "user_3": {"level": "child", "style": "fun"},
    }
    return profiles.get(user_id, {"level": "default", "style": "normal"})

@dynamic_prompt
def user_profile_prompt(request: ModelRequest) -> str:
    """根据用户画像动态调整提示词"""
    user_id = request.runtime.context.get("user_id", "user_1")
    profile = get_user_profile(user_id)
    
    base = "你是一个助手。"
    if profile["level"] == "expert":
        return f"{base} 回答专业深入，使用术语。"
    elif profile["level"] == "beginner":
        return f"{base} 回答简单易懂，避免术语。"
    elif profile["level"] == "child":
        return f"{base} 用讲故事的方式，有趣生动。"
    return base

# ============================================
# 创建 Agent（使用自动推断方式）
# ============================================
agent = create_agent(
    model=model,
    tools=[calculator],
    middleware=[auto_infer_prompt],  # 使用自动推断方式
)

def demo_auto_infer():
    """演示自动推断方式"""
    print("=" * 50)
    print("实际应用 1：自动推断用户意图")
    print("=" * 50)
    
    test_inputs = [
        "2+2等于几？",
        "用python写一个快速排序",
        "翻译：你好世界",
        "今天天气怎么样？",
    ]
    
    for input_text in test_inputs:
        print(f"\n用户输入: {input_text}")
        result = agent.invoke({"messages": [HumanMessage(content=input_text)]})
        print(f"回答: {result['messages'][-1].content[:80]}...")

def demo_user_profile():
    """演示用户画像方式"""
    print("\n" + "=" * 50)
    print("实际应用 2：用户画像动态提示词")
    print("=" * 50)
    
    agent_profile = create_agent(
        model=model,
        tools=[calculator],
        middleware=[user_profile_prompt],
        context_schema=dict,
    )
    
    user_input = "什么是勾股定理？"
    
    for user_id in ["user_1", "user_2", "user_3"]:
        print(f"\n用户: {user_id}")
        result = agent_profile.invoke(
            {"messages": [HumanMessage(content=user_input)]},
            context={"user_id": user_id}
        )
        print(f"回答: {result['messages'][-1].content[:80]}...")

if __name__ == "__main__":
    demo_auto_infer()
    demo_user_profile()
