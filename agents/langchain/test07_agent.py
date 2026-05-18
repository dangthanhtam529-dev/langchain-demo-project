import base64
from langchain.chat_models import init_chat_model
from langchain.tools import tool

IMAGE_PATH = "./image/image.png"

model = init_chat_model(
    model="qwen3.5:0.8b",  
    model_provider="ollama",
    base_url="http://localhost:11434",  # Ollama 默认端口
    temperature=0.8
)

with open(IMAGE_PATH, "rb") as f:
    image_base64 = base64.b64encode(f.read()).decode("utf-8")

@tool
def get_image_description() -> str:
    """识别 ./image/image.png 图片中的内容并返回描述。
    
    Returns:
        图片内容的描述
    """
    messages = [
        ("human", [
            {"type": "text", "text": "请识别这张图片的内容并简洁描述。"},
            {"type": "image_url", "image_url": f"data:image/png;base64,{image_base64}"}
        ])
    ]
    result = model.invoke(messages)
    return result.content

from langchain.agents import create_agent

agent = create_agent(
    model=model,    
    tools=[get_image_description],
    system_prompt="""
你是一个web自动化助手。

你有以下工具可用：
- get_image_description: 识别 ./image/image.png 图片内容（无需参数）

当用户要求识别图片时，直接调用 get_image_description 工具获取结果并返回给用户。
"""
)

for chunk in agent.stream({"input": "请识别 ./image/image.png 这张图片的内容。"}):
    if isinstance(chunk, dict):
        if "model" in chunk and "messages" in chunk["model"]:
            for msg in chunk["model"]["messages"]:
                if hasattr(msg, "content") and msg.content:
                    print(msg.content, end="", flush=True)
    elif hasattr(chunk, "content"):
        print(chunk.content, end="", flush=True)