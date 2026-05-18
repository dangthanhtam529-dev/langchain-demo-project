"""
test06_agent.py - 使用本地 Ollama 模型
需要：
1. 安装 Ollama 软件：https://ollama.com/download
2. 下载模型：ollama pull qwen3.5
3. 确保 Ollama 服务在运行：ollama serve
"""


from langchain_core.messages import SystemMessage, HumanMessage
from langchain.chat_models import init_chat_model

# 使用本地 Ollama 模型
# 模型名称必须与 ollama list 中显示的完全一致
model = init_chat_model(
    model="qwen3.5:0.8b",  # 注意是冒号，不是破折号！
    model_provider="ollama",
    base_url="http://localhost:11434",  # Ollama 默认端口
    temperature=0.8
)

conversation = [
    SystemMessage(content="你是一个专业的文学爱好者"),
    HumanMessage(content="你觉得中国古代最好的五位诗人是谁？")
]

result = model.invoke(conversation)
print(result.content)
