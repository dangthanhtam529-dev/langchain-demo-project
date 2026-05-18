# 批量调用
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
questions = ["中国最好吃的巧克力", "中国朝代更迭顺序"]
results = model.batch(questions)

# 批量调用的结果可能是列表或字符串列表
# 需要根据实际返回类型来处理
for i, result in enumerate(results):
    print(f"问题 {i+1}: {questions[i]}")
    
    # 判断结果类型并正确打印
    if isinstance(result, str):
        # 如果是字符串，直接打印
        print(f"回答: {result}")
    elif hasattr(result, 'content'):
        # 如果是对象，访问 content 属性
        print(f"回答: {result.content}")
    else:
        # 其他类型，转换为字符串
        print(f"回答: {str(result)}")
    
    print("-" * 50)  # 分隔线，让输出更清晰
