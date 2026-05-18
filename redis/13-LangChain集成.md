# 第 13 章：在 LangChain 项目中使用 Redis

> 本章目标：学会在 LangChain 项目中用 Redis 做缓存、消息历史和向量存储。

---

## 一、Redis 在 AI 项目中的角色

在 LangChain 项目中，Redis 通常扮演以下角色：

```
┌─────────────────────────────────────────────┐
│              LangChain 应用                  │
│                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │  LLM API │  │  Redis   │  │  数据库   │  │
│  │ (OpenAI) │  │ (缓存/记忆)│  │ (MySQL)  │  │
│  └──────────┘  └──────────┘  └──────────┘  │
│       ↑             ↑             ↑         │
│       │ 慢且贵      │ 快且便宜    │ 持久化    │
│       └─────────────┴─────────────┘         │
└─────────────────────────────────────────────┘
```

**Redis 的优势：**
- 速度快，适合缓存 LLM 响应
- 支持过期时间，自动清理旧数据
- 数据结构丰富，适合存储对话历史

---

## 二、安装依赖

```bash
pip install redis langchain langchain-community langchain-openai
```

---

## 三、作为 LLM 缓存

### 为什么需要缓存？

LLM API 调用：
- **慢**：每次请求需要几百毫秒到几秒
- **贵**：每次调用都要花钱
- **相同输入得到相同输出**：可以缓存

### 基本用法

```python
import redis
from langchain_community.cache import RedisCache
from langchain_core.globals import set_llm_cache
from langchain_openai import ChatOpenAI

# 设置 Redis 缓存
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
set_llm_cache(RedisCache(redis_=redis_client))

# 创建 LLM
llm = ChatOpenAI(model='gpt-4o-mini')

# 第一次调用（会请求 API）
print('第一次调用...')
response1 = llm.invoke('1+1等于几？')
print(response1.content)

# 第二次调用相同输入（会走缓存）
print('\n第二次调用...')
response2 = llm.invoke('1+1等于几？')
print(response2.content)
```

**效果：**
- 第一次：请求 OpenAI API，耗时约 1 秒
- 第二次：从 Redis 读取缓存，耗时约 1 毫秒

### 缓存的原理

```
输入: "1+1等于几？"
      ↓
   计算哈希值
      ↓
   存入 Redis: key=哈希值, value=LLM响应
      ↓
下次相同输入 → 计算相同哈希 → 从 Redis 读取 → 直接返回
```

---

## 四、作为聊天消息历史

### 基本用法

```python
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage

# 创建消息历史（session_id 用于区分不同用户/会话）
history = RedisChatMessageHistory(
    session_id='user:123',
    url='redis://localhost:6379/0'
)

# 添加用户消息
history.add_user_message("你好，帮我介绍一下 Python")

# 添加 AI 回复
history.add_ai_message("Python 是一种广泛使用的高级编程语言...")

# 添加更多消息
history.add_user_message("它有什么特点？")
history.add_ai_message("Python 的特点包括：1. 语法简洁...")

# 获取所有历史消息
for msg in history.messages:
    print(f'{msg.type}: {msg.content[:50]}...')
```

### 结合 LLM 使用

```python
import redis
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

# 创建 LLM
llm = ChatOpenAI(model='gpt-4o-mini')

# 创建消息历史
chat_history = RedisChatMessageHistory(
    session_id='user:123',
    url='redis://localhost:6379/0'
)

# 创建提示词模板
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个友好的助手，用简洁的语言回答问题。"),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])

# 创建链
chain = prompt | llm | StrOutputParser()

# 对话
def chat(user_input):
    # 获取历史消息
    history_messages = chat_history.messages

    # 调用链
    response = chain.invoke({
        "input": user_input,
        "history": history_messages
    })

    # 保存到历史
    chat_history.add_user_message(user_input)
    chat_history.add_ai_message(response)

    return response

# 测试对话
print('用户: Python 是什么？')
response = chat('Python 是什么？')
print(f'AI: {response}\n')

print('用户: 它难学吗？')
response = chat('它难学吗？')
print(f'AI: {response}\n')

print('用户: 能用来做什么？')
response = chat('能用来做什么？')
print(f'AI: {response}')
```

---

## 五、作为向量存储

### 什么是向量存储？

向量存储用于**相似度搜索**，是 RAG（检索增强生成）的核心组件。

```
用户问题 → 转成向量 → 在向量库中找最相似的文档 → 用这些文档回答用户
```

### 基本用法

```python
from langchain_community.vectorstores import Redis
from langchain_openai import OpenAIEmbeddings

# 创建 Embeddings
embeddings = OpenAIEmbeddings()

# 创建文档
texts = [
    "Python 是一种广泛使用的高级编程语言",
    "Redis 是一个内存数据结构存储",
    "LangChain 是构建 LLM 应用的框架",
    "向量数据库用于存储和检索向量",
    "RAG 是检索增强生成的缩写"
]

# 存入 Redis 向量存储
vectorstore = Redis.from_texts(
    texts=texts,
    embedding=embeddings,
    redis_url="redis://localhost:6379",
    index_name="my_docs"
)

# 相似度搜索
results = vectorstore.similarity_search("什么是编程语言", k=2)

for doc in results:
    print(doc.page_content)
```

### 结合 LLM 实现 RAG

```python
from langchain_community.vectorstores import Redis
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 初始化组件
embeddings = OpenAIEmbeddings()
llm = ChatOpenAI(model='gpt-4o-mini')

# 假设已经存入了文档
vectorstore = Redis.from_existing_index(
    embedding=embeddings,
    redis_url="redis://localhost:6379",
    index_name="my_docs"
)

# 检索相关文档
def get_context(question):
    docs = vectorstore.similarity_search(question, k=3)
    return "\n".join([doc.page_content for doc in docs])

# 创建 RAG 链
prompt = ChatPromptTemplate.from_template("""
根据以下参考资料回答问题：

参考资料：
{context}

问题：{question}

请根据参考资料回答问题：
""")

rag_chain = prompt | llm | StrOutputParser()

# 使用
question = "Python 是什么？"
context = get_context(question)
answer = rag_chain.invoke({"context": context, "question": question})
print(answer)
```

---

## 六、实战：带记忆的 AI 助手

```python
import redis
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

class AIAssistant:
    """带记忆的 AI 助手"""

    def __init__(self, user_id):
        self.user_id = user_id
        self.llm = ChatOpenAI(model='gpt-4o-mini')

        # Redis 消息历史
        self.chat_history = RedisChatMessageHistory(
            session_id=f'user:{user_id}',
            url='redis://localhost:6379/0'
        )

        # 提示词模板
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一个专业的 AI 助手。你有以下用户信息：{user_info}"),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}")
        ])

        # 链
        self.chain = self.prompt | self.llm | StrOutputParser()

        # Redis 用户信息
        self.r = redis.Redis(host='localhost', port=6379, decode_responses=True)

    def set_user_info(self, info):
        """设置用户信息"""
        self.r.hset(f'user:{self.user_id}:info', mapping=info)

    def get_user_info(self):
        """获取用户信息"""
        info = self.r.hgetall(f'user:{self.user_id}:info')
        if not info:
            return "无"
        return ", ".join([f"{k}: {v}" for k, v in info.items()])

    def chat(self, message):
        """对话"""
        # 获取历史
        history = self.chat_history.messages

        # 获取用户信息
        user_info = self.get_user_info()

        # 调用
        response = self.chain.invoke({
            "user_info": user_info,
            "history": history,
            "input": message
        })

        # 保存历史
        self.chat_history.add_user_message(message)
        self.chat_history.add_ai_message(response)

        return response

    def get_history(self):
        """获取对话历史"""
        return self.chat_history.messages

    def clear_history(self):
        """清空对话历史"""
        self.chat_history.clear()

# 使用示例
assistant = AIAssistant('user:001')

# 设置用户信息
assistant.set_user_info({
    'name': '张三',
    'role': 'Python 初学者',
    'interest': 'AI 开发'
})

# 对话
questions = [
    '你好，我是张三',
    '我想学习 Python，有什么建议？',
    '我对 AI 开发很感兴趣，应该从哪里开始？'
]

for q in questions:
    print(f'用户: {q}')
    response = assistant.chat(q)
    print(f'AI: {response}\n')

# 查看历史
print('=== 对话历史 ===')
for msg in assistant.get_history():
    print(f'{msg.type}: {msg.content[:50]}...')
```

---

## 七、实战：缓存优化

```python
import redis
import time
from langchain_community.cache import RedisCache
from langchain_core.globals import set_llm_cache
from langchain_openai import ChatOpenAI

class CacheManager:
    """缓存管理器"""

    def __init__(self):
        self.r = redis.Redis(host='localhost', port=6379, decode_responses=True)

    def setup_cache(self, ttl=3600):
        """设置 LLM 缓存，带过期时间"""
        # 注意：langchain 的 RedisCache 默认不支持 TTL
        # 可以用自定义缓存逻辑
        set_llm_cache(RedisCache(redis_=self.r))
        print(f'LLM 缓存已启用')

    def get_cache_stats(self):
        """获取缓存统计信息"""
        # 获取缓存键数量
        cache_keys = self.r.keys('langchain_cache:*')
        print(f'缓存条目数: {len(cache_keys)}')

        # 获取 Redis 内存使用
        info = self.r.info('memory')
        used_memory = info.get('used_memory_human', 'unknown')
        print(f'内存使用: {used_memory}')

    def clear_cache(self):
        """清空 LLM 缓存"""
        cache_keys = self.r.keys('langchain_cache:*')
        if cache_keys:
            self.r.delete(*cache_keys)
            print(f'已清空 {len(cache_keys)} 个缓存条目')
        else:
            print('没有缓存需要清理')

# 使用示例
cache_mgr = CacheManager()
cache_mgr.setup_cache()

# 使用 LLM（自动缓存）
llm = ChatOpenAI(model='gpt-4o-mini')

# 第一次调用
start = time.time()
response = llm.invoke('解释一下什么是机器学习')
print(f'第一次耗时: {time.time() - start:.2f}秒')
print(f'回答: {response.content[:100]}...\n')

# 第二次调用（缓存命中）
start = time.time()
response = llm.invoke('解释一下什么是机器学习')
print(f'第二次耗时: {time.time() - start:.2f}秒')
print(f'回答: {response.content[:100]}...\n')

# 查看缓存统计
cache_mgr.get_cache_stats()
```

---

## 八、本章小结

### Redis 在 LangChain 中的三种用法

| 用途 | 类 | 说明 |
|------|-----|------|
| **LLM 缓存** | `RedisCache` | 缓存相同的输入输出 |
| **消息历史** | `RedisChatMessageHistory` | 存储对话历史 |
| **向量存储** | `Redis` | 存储文档向量，支持相似度搜索 |

### 核心理解

1. 缓存可以**显著降低 API 调用成本**
2. 消息历史支持**多会话**，用 `session_id` 区分
3. 向量存储是 **RAG 应用**的核心组件

### 总结

恭喜你完成了 Redis 的学习！从入门到实战，你已经掌握了：

- 5 种核心数据结构
- 事务、管道、Lua 脚本
- 在 LangChain 项目中的实际应用

继续实践，你会越来越熟练！

---

> 💡 **动手练习**：
> 1. 用 RedisChatMessageHistory 实现一个多轮对话
> 2. 用 RedisCache 缓存 LLM 响应
> 3. 用 Redis 向量存储实现简单的 RAG 应用
