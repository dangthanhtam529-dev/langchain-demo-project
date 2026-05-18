"""
test12_agent.py - 使用 TypedDict 进行结构化输出
让模型返回符合 TypedDict 定义的数据格式
"""

from typing_extensions import TypedDict, Annotated
from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, HumanMessage
import os
from dotenv import load_dotenv


load_dotenv() 

model = init_chat_model(
    "glm-4.7",
    model_provider="openai",
    base_url="https://open.bigmodel.cn/api/paas/v4",
    api_key=os.getenv("ZHIPUAI_API_KEY"),
)



class MovieDict(TypedDict):
    """电影信息"""
    title: Annotated[str, ..., "电影名称"]
    year: Annotated[int, ..., "上映年份"]
    director: Annotated[str, ..., "导演"]
    rating: Annotated[float, ..., "评分（满分 10 分）"]




# model_with_structure = model.with_structured_output(MovieDict,include_raw=True)

# print(model_with_structure.invoke("请介绍一下电影《盗梦空间》的信息"))

print(model.profile)