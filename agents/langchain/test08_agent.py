from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
import os
from dotenv import load_dotenv  

load_dotenv()

model = init_chat_model(
    model="MiniMax-M2.7",
    max_tokens=1000,
    model_provider="openai",
    base_url="https://api.minimaxi.com/v1",
    api_key=os.getenv("MINIMAX_API_KEY"),
)

agent = create_agent(
    model=model,
    system_prompt="你是一个高效的助手，回答精简直接但不失专业性。"
)
prompt = """
人工智能（Artificial Intelligence，简称AI）是计算机科学的一个分支，它企图了解智能的实质，
并生产出一种新的能以人类智能相似的方式做出反应的智能机器。该领域的研究包括机器人、
语言识别、图像识别、自然语言处理和专家系统等。人工智能从诞生以来，理论和技术日益成熟，
应用领域也不断扩大，可以设想，未来人工智能带来的科技产品，将会是人类智慧的"容器"。
人工智能可以对人的意识、思维的信息过程的模拟。人工智能不是人的智能，但能像人那样思考、
也可能超过人的智能。人工智能是一门极富挑战性的科学，从事这项工作的人必须懂得计算机知识，
心理学和哲学。人工智能是包括十分广泛的科学，它由不同的领域组成，如机器学习，计算机视觉等等。
"""



result = agent.invoke(
    {"messages": [{"role": "user", "content": f"请你总结一下这段话的内容：{prompt}"}]}
)
print(result["messages"][-1].content)