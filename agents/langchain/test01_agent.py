"""
test01_agent.py - 第一个 LangChain Agent 示例
这是一个入门级的 LangChain Agent 示例，演示了如何：
1. 定义自定义工具
2. 初始化聊天模型
3. 创建 Agent 并绑定工具
4. 调用 Agent 处理用户请求

学习重点：
- Agent 的基本工作流程
- 工具的定义和使用
- 模型配置和环境变量管理
"""

# ============================================
# 环境配置
# ============================================
# 加载 .env 文件中的环境变量
# dotenv 库会读取项目根目录下的 .env 文件
# 这样可以避免在代码中硬编码敏感信息（如 API Key）
from dotenv import load_dotenv
import os

load_dotenv()

# ============================================
# LangChain 核心模块导入
# ============================================
# create_agent: 创建 Agent 实例的核心函数
# tool: 装饰器，用于将 Python 函数定义为 Agent 可调用的工具
# init_chat_model: 初始化聊天模型的便捷函数
from langchain.agents import create_agent
from langchain.tools import tool
from langchain.chat_models import init_chat_model

# 标准库导入
import requests


# ============================================
# 1. 定义工具（Tools）
# ============================================
# 使用 @tool 装饰器将普通函数转换为 Agent 可用的工具
# 工具是 Agent 与外部世界交互的桥梁
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


# ============================================
# 2. 初始化模型（Model）
# ============================================
# 使用 init_chat_model 初始化聊天模型
# 支持多种模型提供商，这里使用智谱AI（Zhipu AI）的 glm-4.7 模型
# 
# 参数说明：
# - model: 模型名称，指定使用哪个 AI 模型
# - model_provider: 模型提供商，这里使用 "openai" 因为智谱AI兼容 OpenAI API 格式
# - base_url: API 端点地址，智谱AI的 OpenAI 兼容接口
# - api_key: 从环境变量读取的 API 密钥
#
# 为什么用 OpenAI provider？
# 智谱AI、Claude 等很多模型提供商都支持 OpenAI 兼容格式
# 这样可以用统一的接口调用不同的模型
model = init_chat_model(
    "glm-4.7",
    model_provider="openai",
    base_url="https://open.bigmodel.cn/api/paas/v4",
    api_key=os.getenv("ZHIPUAI_API_KEY"),
)


# ============================================
# 3. 创建 Agent
# ============================================
# create_agent 函数将模型和工具组合成一个智能 Agent
# 
# 主要参数：
# - model: 已初始化的聊天模型实例
# - tools: Agent 可用的工具列表，这里传入天气查询工具
# - system_prompt: 系统提示词，定义 Agent 的角色和行为规则
#
# system_prompt 的作用：
# - 告诉 Agent 它的身份是什么（天气助手）
# - 指导 Agent 如何使用工具（先查询再回答）
# - 影响 Agent 的回答风格（友好、简洁等）
agent = create_agent(
    model=model,
    tools=[get_current_weather],
    system_prompt="你是一个友好的天气助手。当用户询问天气时，使用 get_weather 工具查询后回答。"
)


# ============================================
# 4. 运行 Agent
# ============================================
# agent.invoke() 是调用 Agent 的主要方式
# 
# 输入格式：
# - 是一个字典，包含 "messages" 键
# - messages 是消息列表，每条消息包含：
#   - role: 角色（"user" 表示用户，"system" 表示系统，"assistant" 表示助手）
#   - content: 消息内容
#
# 输出格式：
# - 返回一个字典，包含处理后的消息列表
# - "messages" 键包含完整的对话历史
# - 可以通过 result["messages"][-1].content 获取最后一条助手回复
result = agent.invoke(
    {"messages": [{"role": "user", "content": "北京今天天气怎么样？"}]}
)


# ============================================
# 5. 输出结果
# ============================================
# 打印 Agent 的最后一条回复
# result["messages"] 包含所有消息，取最后一个元素就是助手的最新回复
print(result["messages"][-1].content)


# ============================================
# 扩展阅读
# ============================================
# 1. 多工具 Agent：可以添加更多工具，如计算器、搜索等
#    agent = create_agent(
#        model=model,
#        tools=[get_weather, calculator, search],
#        ...
#    )
#
# 2. 记忆功能：让 Agent 记住对话历史
#    from langgraph.checkpoint.memory import InMemorySaver
#    checkpointer = InMemorySaver()
#    agent = create_agent(..., checkpointer=checkpointer)
#
# 3. 流式输出：实时显示 Agent 的思考过程
#    for chunk in agent.stream({"messages": [...] }):
#        print(chunk)
