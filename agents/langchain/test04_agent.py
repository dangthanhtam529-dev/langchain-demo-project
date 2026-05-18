# 流式调用
from langchain.chat_models import init_chat_model
import os
from dotenv import load_dotenv

load_dotenv() 

model = init_chat_model(
    "glm-4.7",
    model_provider="openai",
    base_url="https://open.bigmodel.cn/api/paas/v4",
    api_key=os.getenv("ZHIPUAI_API_KEY"),
)

# 流式调用
# 注意：不同模型的流式输出格式可能不同
# 这里提供两种常见的处理方式

# 方式一：直接打印（适用于简单字符串输出）
# print("方式一 - 直接打印：")
# for chunk in model.stream("给我一首刘禹锡的经典诗"):
#     if isinstance(chunk, str):
#         print(chunk, end="", flush=True)
#     else:
#         # 如果是其他类型，直接打印
#         print(chunk, end="", flush=True)

