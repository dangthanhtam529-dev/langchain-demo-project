# 静态提示词设计
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy, ProviderStrategy
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langchain.tools import tool

from dotenv import load_dotenv
import os 

load_dotenv()

def create_demo_prompt(role,tools_info,constraints):
   system_prompt = f"""
 你是一个{role}，你的任务是根据用户输入和工具信息，生成符合要求的输出。
 工具信息：{tools_info}
 约束条件：{constraints}
   """
   return system_prompt

@tool
def calculator(expression: str) -> str:
    """执行数学计算"""
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return f"计算结果: {result}"
    except Exception as e:
        return f"计算错误: {e}"

model = init_chat_model(
    model="MiniMax-M2.7",
    model_provider="openai",
    base_url="https://api.minimaxi.com/v1",
    api_key=os.getenv("MINIMAX_API_KEY")

)

system_prompt = create_demo_prompt("专业的数学老师","执行数学计算","回答简洁明了")



agent = create_agent(
    model=model,
    tools=[calculator],
    system_prompt=system_prompt
)

for chunk in agent.stream({"messages": [HumanMessage(content="2+2等于几？")]}):
    # chunk 格式: {'model': {'messages': [...]}} 或 {'tools': {'messages': [...]}}
    if 'model' in chunk:
        # AI 模型回复
        messages = chunk['model']['messages']
        for msg in messages:
            if hasattr(msg, 'content') and msg.content:
                # 提取纯文本内容
                print(msg.content, end="", flush=True)
    elif 'tools' in chunk:
        # 工具调用结果（可选显示）
        messages = chunk['tools']['messages']
        for msg in messages:
            if hasattr(msg, 'content') and msg.content:
                print(f"\n[工具结果]: {msg.content}", end="", flush=True)



