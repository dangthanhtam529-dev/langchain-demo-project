# 裁剪信息，保留最开始以及最近的消息
from langchain.messages import RemoveMessage
from langchain.chat_models import init_chat_model
from langgraph.graph.message import REMOVE_ALL_MESSAGES
from langchain.agents import create_agent, AgentState
from langchain_core.messages import HumanMessage
import os 


from langchain.agents.middleware import before_model
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.runtime import Runtime
from typing import Any
from dotenv import load_dotenv
load_dotenv() 


@before_model
def remove_all_messages(state: AgentState, runtime: Runtime) -> dict[str, Any]:
    messages = state["messages"]
    if len(messages) < 3 :
        return None
    first_message = messages[0]
    last_message = messages[-3:] if len(messages)%2 == 0 else messages[-2:]
    new_messages = [first_message] + last_message
    return {
        "messages": [
            RemoveMessage(id=REMOVE_ALL_MESSAGES),  # 先清除所有消息
            *new_messages  # 再把保留的消息解包进来
        ]
    }

model = init_chat_model(
    model="MiniMax-M2.7",
    model_provider="openai",
    base_url="https://api.minimaxi.com/v1",
    api_key=os.getenv("MINIMAX_API_KEY")
)

agent = create_agent(
    model=model,
    system_prompt="你是一个生活助手助手，根据用户的问题回答问题。回答要专业、客观。",
    checkpointer=InMemorySaver()
)
config = {"configurable": {"thread_id": "123456"}}

agent.invoke({"messages": [HumanMessage(content="我叫张三，我是一个喜欢安静的人")]}, config=config)
agent.invoke({"messages": [HumanMessage(content="你觉得我的性格适合听什么音乐")]}, config=config)
agent.invoke({"messages": [HumanMessage(content="有哪些好玩的地方推荐给我")]}, config=config)
agent.invoke({"messages": [HumanMessage(content="给我推荐一款鸡尾酒")]}, config=config)
agent.invoke({"messages": [HumanMessage(content="你觉得鸡尾酒的口味如何")]}, config=config)

# 即使经过多轮对话，Agent 仍然能记住名字
final_response = agent.invoke({"messages": [HumanMessage(content="我叫什么名字")]}, config=config)
print(final_response["messages"][-1].content)
