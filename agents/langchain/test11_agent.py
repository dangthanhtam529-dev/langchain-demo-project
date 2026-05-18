"""
test11_agent.py - 使用结构化输出
让模型按照约定的 Pydantic 数据格式输出 JSON
"""

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
import json

load_dotenv()

model = init_chat_model(
    model="MiniMax-M2.7",
    model_provider="openai",
    base_url="https://api.minimaxi.com/v1",
    api_key=os.getenv("MINIMAX_API_KEY"),
    timeout=120,
    max_retries=3
)


class Movie(BaseModel):
    """电影信息结构"""
    title: str = Field(description="电影的标题")
    director: str = Field(description="电影的导演")
    actors: str = Field(description="电影的演员，用逗号分隔")
    genre: str = Field(description="电影的类型")
    release_date: str = Field(description="电影的上映日期")


print("=" * 50)
print("方式1：使用 with_structured_output")
print("=" * 50)

model_with_schema = model.with_structured_output(Movie)

messages = [
    SystemMessage(content="你是一个电影推荐助手。你必须且只能输出一个有效的 JSON 对象，不要输出任何其他内容（如思考过程、解释等）。\n\nJSON 格式：\n{\"title\": \"电影标题\", \"director\": \"导演\", \"actors\": \"演员1, 演员2\", \"genre\": \"类型\", \"release_date\": \"上映日期\"}\n\n直接输出 JSON，不要有其他文字。"),
    HumanMessage(content="请推荐一部动作电影")
]

try:
    result = model_with_schema.invoke(messages)
    print(f"电影标题: {result.title}")
    print(f"导演: {result.director}")
    print(f"演员: {result.actors}")
    print(f"类型: {result.genre}")
    print(f"上映日期: {result.release_date}")
except Exception as e:
    print(f"结构化输出失败: {e}")
    print("\n尝试方式2...")

print("\n" + "=" * 50)
print("方式2：直接解析 JSON（更可靠）")
print("=" * 50)

# 不使用 with_structured_output，而是直接让模型输出 JSON 然后手动解析
messages2 = [
    SystemMessage(content="你是一个电影推荐助手。请根据用户请求推荐一部电影，然后按以下 JSON 格式输出：\n{\"title\": \"电影标题\", \"director\": \"导演\", \"actors\": \"演员1, 演员2\", \"genre\": \"类型\", \"release_date\": \"上映日期\"}\n\n重要：你必须只输出这个 JSON 对象，不要输出任何其他内容！"),
    HumanMessage(content="请推荐一部动作电影")
]

try:
    result_text = model.invoke(messages2)
    content = result_text.content if hasattr(result_text, 'content') else str(result_text)

    # 尝试提取 JSON
    print("模型原始输出:")
    print(content)
    print("-" * 50)

    # 简单解析：提取 JSON 部分
    json_str = content.strip()
    # 如果有思考过程，尝试提取 ```json ... ``` 或 ```...``` 中的内容
    if "```json" in json_str:
        json_str = json_str.split("```json")[1].split("```")[0]
    elif "```" in json_str:
        json_str = json_str.split("```")[1].split("```")[0]

    json_str = json_str.strip()
    movie_data = json.loads(json_str)

    print("解析后的数据：")
    print(f"电影标题: {movie_data['title']}")
    print(f"导演: {movie_data['director']}")
    print(f"演员: {movie_data['actors']}")
    print(f"类型: {movie_data['genre']}")
    print(f"上映日期: {movie_data['release_date']}")

except Exception as e:
    print(f"JSON 解析失败: {e}")
    print("\n方式3：纯文本输出（保底）")
    print("-" * 50)
    result_text = model.invoke(messages)
    print(result_text.content if hasattr(result_text, 'content') else result_text)
