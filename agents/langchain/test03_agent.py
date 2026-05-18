# 模型的调用，第一种形式invoke同步调用
from langchain.agents import create_agent
from dotenv import load_dotenv
import os

load_dotenv()
from langchain.chat_models import init_chat_model

model = init_chat_model(
    "glm-4.7",
    model_provider="openai",
    base_url="https://open.bigmodel.cn/api/paas/v4",
    api_key=os.getenv("ZHIPUAI_API_KEY"),
)

# 调用模型,注意这里不是智能体,只是调用模型,没有智能体的逻辑
# print(model.invoke("我今天心情真不错"))


# 字典格式的消息列表
# conversation = [
#     {"role": "system", "content": "你是一个翻译助手，你的任务是将用户输入的文本翻译成英文。"},
#     {"role": "user", "content": "翻译：我今天心情真不错"},
#     {"role": "assistant", "content": "I feeling good today"},
#     {"role": "user", "content": "翻译：我一定会成功的"}
    
#    ]
# result = model.invoke(conversation)
# print(result.content)


# 消息对象格式
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

conversation = [
  SystemMessage(content="你是一个翻译助手，你的任务是将用户输入的文本翻译成英文。"),
  HumanMessage(content="翻译：我今天心情真不错"),
  AIMessage(content="I feeling good today"),
  HumanMessage(content="翻译：我一定会成功的"),
]
result = model.invoke(conversation)
print(result.content)