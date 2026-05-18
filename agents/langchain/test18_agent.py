from pydantic import BaseModel, Field
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy, ProviderStrategy
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import os 

load_dotenv()



class MovieInfo(BaseModel):
    title: str = Field(description="电影名称")
    year: int = Field(description="上映年份")
    director: str = Field(description="导演")

model = init_chat_model(
    model="glm-4.7",
    model_provider="openai",
    base_url="https://open.bigmodel.cn/api/paas/v4",
    api_key=os.getenv("ZHIPUAI_API_KEY"),
)



## 方式 1：自动选择（推荐）
agent = create_agent(model,  response_format=MovieInfo)

# # 方式 2：强制使用 ToolStrategy
# agent = create_agent(model, tools, response_format=ToolStrategy(MovieInfo))

# # 方式 3：使用 ProviderStrategy（需要模型支持）
# agent = create_agent(model, tools, response_format=ProviderStrategy(MovieInfo))

print(agent.invoke({"messages": [HumanMessage(content="你好，我想知道最近上映的电影信息")]})["messages"][-1].content)