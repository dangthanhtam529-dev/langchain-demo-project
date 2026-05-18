# Redis 学习文档

> 本文档基于 Redis 官方文档（https://redis.io/docs/）编写，内容涵盖从入门到高级的完整知识体系。

---

## 目录

- [初级篇：Redis 入门](#初级篇redis-入门)
  - [第 1 章：Redis 是什么](#第-1-章redis-是什么)
  - [第 2 章：安装与启动](#第-2-章安装与启动)
  - [第 3 章：连接 Redis](#第-3-章连接-redis)
  - [第 4 章：第一个 Redis 命令](#第-4-章第一个-redis-命令)
  - [第 5 章：Python 客户端 redis-py](#第-5-章python-客户端-redis-py)
- [中级篇：核心数据结构](#中级篇核心数据结构)
  - [第 6 章：字符串（String）](#第-6-章字符串string)
  - [第 7 章：哈希（Hash）](#第-7-章哈希hash)
  - [第 8 章：列表（List）](#第-8-章列表list)
  - [第 9 章：集合（Set）](#第-9-章集合set)
  - [第 10 章：有序集合（Sorted Set）](#第-10-章有序集合sorted-set)
  - [第 11 章：键的过期与持久化](#第-11-章键的过期与持久化)
- [高级篇：进阶特性](#高级篇进阶特性)
  - [第 12 章：发布与订阅（Pub/Sub）](#第-12-章发布与订阅pubsub)
  - [第 13 章：事务（Transaction）](#第-13-章事务transaction)
  - [第 14 章：Lua 脚本](#第-14-章lua-脚本)
  - [第 15 章：管道（Pipeline）](#第-15-章管道pipeline)
  - [第 16 章：Redis JSON](#第-16-章redis-json)
  - [第 17 章：Redis Search 全文搜索](#第-17-章redis-search-全文搜索)
  - [第 18 章：持久化机制](#第-18-章持久化机制)
  - [第 19 章：在 LangChain 项目中使用 Redis](#第-19-章在-langchain-项目中使用-redis)

---

# 初级篇：Redis 入门

## 第 1 章：Redis 是什么

### 1.1 核心定义

Redis（Remote Dictionary Server）是一个**开源的内存数据结构存储**。官方定义它为：

> An in-memory data structure store

它的核心特点：

- **内存存储**：数据保存在内存中，读写速度极快（亚毫秒级延迟）
- **键值模型**：通过键（key）来存取值（value）
- **多种数据结构**：不只是简单的字符串，还支持哈希、列表、集合等
- **持久化**：支持将内存数据保存到磁盘
- **单线程模型**：避免了多线程竞争，命令执行是原子的

### 1.2 典型应用场景

| 场景 | 说明 |
|------|------|
| **缓存** | 最常见的用途，缓存数据库查询结果 |
| **会话存储** | 保存用户登录状态 |
| **消息队列** | 使用 List 实现简单的消息队列 |
| **排行榜** | 使用 Sorted Set 实现实时排名 |
| **计数器** | 使用 INCR 命令实现访问统计 |
| **实时分析** | 高速写入和读取实时数据 |

### 1.3 Redis vs 传统数据库

```
传统数据库（MySQL）：
磁盘存储 → 慢但持久 → 适合复杂查询

Redis：
内存存储 → 快但容量有限 → 适合高速读写
```

两者通常**配合使用**，而不是互相替代。

---

## 第 2 章：安装与启动

### 2.1 Windows 安装

Redis 官方不直接支持 Windows，但有以下几种方式：

**方式 1：使用 WSL（推荐）**
```bash
# 在 WSL 中安装
sudo apt-get update
sudo apt-get install redis-server
```

**方式 2：使用 Docker（最简单）**
```bash
docker run -d --name redis -p 6379:6379 redis:latest
```

**方式 3：使用 Microsoft 维护的 Windows 版本**
从 https://github.com/microsoftarchive/redis/releases 下载

### 2.2 Linux 安装
```bash
sudo apt-get update
sudo apt-get install redis-server
```

### 2.3 macOS 安装
```bash
brew install redis
```

### 2.4 启动与停止

```bash
# 启动 Redis 服务器
redis-server

# 启动时指定配置文件
redis-server /path/to/redis.conf

# 停止 Redis
redis-cli shutdown
```

### 2.5 验证安装

```bash
redis-cli ping
# 如果返回 PONG，说明 Redis 正常运行
```

---

## 第 3 章：连接 Redis

### 3.1 使用 redis-cli 连接

`redis-cli` 是 Redis 自带的命令行客户端：

```bash
# 连接本地默认端口
redis-cli

# 连接指定主机和端口
redis-cli -h 127.0.0.1 -p 6379

# 带密码连接
redis-cli -h 127.0.0.1 -p 6379 -a your_password
```

连接成功后，你会看到类似这样的提示符：
```
127.0.0.1:6379>
```

### 3.2 测试连接

```
127.0.0.1:6379> PING
PONG
```

`PING` 命令用于测试连接是否正常，正常会返回 `PONG`。

---

## 第 4 章：第一个 Redis 命令

### 4.1 基本操作：SET 和 GET

这是 Redis 最基础的两个命令：

```
127.0.0.1:6379> SET name "张三"
OK

127.0.0.1:6379> GET name
"张三"
```

**语法说明：**
- `SET key value`：将值保存到指定键
- `GET key`：获取指定键的值

### 4.2 数字操作：INCR

```
127.0.0.1:6379> SET counter 0
OK

127.0.0.1:6379> INCR counter
(integer) 1

127.0.0.1:6379> INCR counter
(integer) 2

127.0.0.1:6379> INCRBY counter 10
(integer) 12
```

**语法说明：**
- `INCR key`：将键的值加 1
- `INCRBY key increment`：将键的值加指定数字

### 4.3 键管理

```
# 检查键是否存在
127.0.0.1:6379> EXISTS name
(integer) 1

# 删除键
127.0.0.1:6379> DEL name
(integer) 1

# 设置过期时间（秒）
127.0.0.1:6379> SET temp "临时数据" EX 60
OK

# 查看剩余生存时间
127.0.0.1:6379> TTL temp
(integer) 45

# 列出所有键
127.0.0.1:6379> KEYS *
1) "counter"
2) "temp"
```

**语法说明：**
- `EXISTS key`：检查键是否存在，返回 1 表示存在，0 表示不存在
- `DEL key`：删除键，返回删除的数量
- `SET key value EX seconds`：设置键的同时指定过期时间
- `TTL key`：查看键的剩余生存时间（秒），-1 表示永不过期，-2 表示键不存在
- `KEYS pattern`：匹配键，`*` 表示所有键

---

## 第 5 章：Python 客户端 redis-py

### 5.1 安装

```bash
pip install redis
```

### 5.2 基本连接

根据官方文档，最简单的连接方式：

```python
import redis

# 连接本地 Redis（默认 localhost:6379）
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# decode_responses=True 让返回值自动解码为字符串，而不是 bytes
```

**参数说明：**
- `host`：Redis 服务器地址
- `port`：端口号，默认 6379
- `db`：数据库编号，Redis 默认有 16 个数据库（0-15）
- `decode_responses`：是否自动将返回的 bytes 解码为字符串

### 5.3 基本操作

```python
import redis

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# 设置和获取
r.set('name', '张三')
print(r.get('name'))  # 输出: 张三

# 数字操作
r.set('counter', 0)
r.incr('counter')       # 加 1
r.incrby('counter', 10) # 加 10
print(r.get('counter'))  # 输出: 11

# 删除
r.delete('name')
print(r.exists('name'))  # 输出: 0
```

### 5.4 连接池

在生产环境中，应该使用连接池来复用连接：

```python
import redis

# 创建连接池
pool = redis.ConnectionPool(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=True,
    max_connections=50  # 最大连接数
)

# 从连接池获取连接
r = redis.Redis(connection_pool=pool)
```

**为什么需要连接池？**
每次创建 Redis 连接都有开销。连接池预先创建一批连接，需要时直接取用，用完后归还，避免频繁创建和销毁连接。

---

# 中级篇：核心数据结构

## 第 6 章：字符串（String）

### 6.1 概述

字符串是 Redis **最基本的数据类型**。Redis 字符串是**二进制安全**的，意味着它可以存储任何数据：文本、图片、序列化对象等。单个字符串最大值为 512MB。

### 6.2 常用命令

```python
import redis
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# SET - 设置值
r.set('name', 'Redis')

# GET - 获取值
print(r.get('name'))  # 输出: Redis

# MSET - 批量设置多个键值对
r.mset({'key1': 'value1', 'key2': 'value2', 'key3': 'value3'})

# MGET - 批量获取多个键的值
print(r.mget(['key1', 'key2', 'key3']))  # 输出: ['value1', 'value2', 'value3']

# GETSET - 设置新值并返回旧值
old_value = r.getset('name', 'NewRedis')
print(f'旧值: {old_value}')  # 输出: 旧值: Redis

# APPEND - 追加字符串
r.set('greeting', 'Hello')
r.append('greeting', ' World')
print(r.get('greeting'))  # 输出: Hello World

# STRLEN - 获取字符串长度
print(r.strlen('greeting'))  # 输出: 11

# GETRANGE - 获取子字符串（类似 substring）
r.set('text', 'Hello World')
print(r.getrange('text', 0, 4))   # 输出: Hello
print(r.getrange('text', 6, 10))  # 输出: World
```

### 6.3 数字操作

```python
# INCR - 自增 1
r.set('views', 100)
r.incr('views')
print(r.get('views'))  # 输出: 101

# INCRBY - 自增指定值
r.incrby('views', 50)
print(r.get('views'))  # 输出: 151

# INCRBYFLOAT - 自增浮点数
r.set('price', 10.5)
r.incrbyfloat('price', 2.3)
print(r.get('price'))  # 输出: 12.8

# DECR - 自减 1
r.decr('views')
print(r.get('views'))  # 输出: 150

# DECRBY - 自减指定值
r.decrby('views', 50)
print(r.get('views'))  # 输出: 100
```

**注意：** 如果键不存在，`INCR` 会将其视为 0 然后加 1。

### 6.4 带过期时间的设置

```python
# 方式 1：SET 时指定过期时间（秒）
r.set('token', 'abc123', ex=3600)  # 1 小时后过期

# 方式 2：SET 时指定过期时间（毫秒）
r.set('token', 'abc123', px=3600000)  # 1 小时后过期

# 方式 3：使用 EXPIRE 命令单独设置
r.set('session', 'user_data')
r.expire('session', 1800)  # 30 分钟后过期

# 方式 4：使用 EXPIREAT 指定具体时间（Unix 时间戳）
import time
r.set('cache', 'data')
r.expireat('cache', int(time.time()) + 3600)  # 1 小时后过期

# 查看剩余时间
print(r.ttl('token'))  # 输出: 剩余秒数，-1 表示永不过期，-2 表示不存在

# 移除过期时间（变为持久化）
r.persist('token')
```

---

## 第 7 章：哈希（Hash）

### 7.1 概述

Hash 是一个**键值对集合**，类似于 Python 的字典。它适合存储对象，比如用户信息、商品详情等。

**为什么用 Hash 而不是多个 String？**

```
方式 1：用多个 String
SET user:1:name "张三"
SET user:1:age "25"
SET user:1:email "zhangsan@example.com"

方式 2：用 Hash（推荐）
HSET user:1 name "张三" age 25 email "zhangsan@example.com"
```

Hash 的优势：
- 更节省内存
- 可以单独操作某个字段
- 语义更清晰

### 7.2 常用命令

```python
import redis
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# HSET - 设置单个字段
r.hset('user:1', 'name', '张三')
r.hset('user:1', 'age', 25)
r.hset('user:1', 'email', 'zhangsan@example.com')

# 或者一次性设置多个字段
r.hset('user:1', mapping={
    'name': '张三',
    'age': 25,
    'email': 'zhangsan@example.com',
    'city': '北京'
})

# HGET - 获取单个字段
print(r.hget('user:1', 'name'))  # 输出: 张三

# HGETALL - 获取所有字段和值
print(r.hgetall('user:1'))
# 输出: {'name': '张三', 'age': '25', 'email': 'zhangsan@example.com', 'city': '北京'}

# HMGET - 获取多个字段
print(r.hmget('user:1', ['name', 'email']))
# 输出: ['张三', 'zhangsan@example.com']

# HDEL - 删除字段
r.hdel('user:1', 'city')
print(r.hgetall('user:1'))
# 输出: {'name': '张三', 'age': '25', 'email': 'zhangsan@example.com'}

# HEXISTS - 判断字段是否存在
print(r.hexists('user:1', 'name'))  # 输出: True
print(r.hexists('user:1', 'city'))  # 输出: False

# HLEN - 获取字段数量
print(r.hlen('user:1'))  # 输出: 3

# HKEYS - 获取所有字段名
print(r.hkeys('user:1'))  # 输出: ['name', 'age', 'email']

# HVALS - 获取所有字段值
print(r.hvals('user:1'))  # 输出: ['张三', '25', 'zhangsan@example.com']

# HINCRBY - 字段值自增
r.hset('user:1', 'score', 100)
r.hincrby('user:1', 'score', 50)
print(r.hget('user:1', 'score'))  # 输出: 150
```

### 7.3 实际应用：用户信息存储

```python
import redis
import json

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

def create_user(user_id, name, email, age):
    """创建用户"""
    r.hset(f'user:{user_id}', mapping={
        'name': name,
        'email': email,
        'age': str(age),
        'created_at': '2024-01-01'
    })
    print(f'用户 {name} 创建成功')

def get_user(user_id):
    """获取用户信息"""
    user_data = r.hgetall(f'user:{user_id}')
    if not user_data:
        print('用户不存在')
        return None
    return user_data

def update_user_field(user_id, field, value):
    """更新用户某个字段"""
    r.hset(f'user:{user_id}', field, value)
    print(f'字段 {field} 已更新')

# 使用示例
create_user('1001', '李四', 'lisi@example.com', 30)
user = get_user('1001')
print(user)
# 输出: {'name': '李四', 'email': 'lisi@example.com', 'age': '30', 'created_at': '2024-01-01'}

update_user_field('1001', 'age', 31)
print(r.hget('user:1001', 'age'))  # 输出: 31
```

---

## 第 8 章：列表（List）

### 8.1 概述

Redis List 是一个**按插入顺序排序的字符串列表**。底层实现是**双向链表**，这意味着从两端插入和删除元素的时间复杂度都是 O(1)。

**典型应用场景：**
- 消息队列
- 最新动态列表
- 分页数据

### 8.2 常用命令

```python
import redis
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# LPUSH - 从左侧（头部）插入
r.lpush('tasks', 'task1')
r.lpush('tasks', 'task2')
r.lpush('tasks', 'task3')
# 列表现在是: ['task3', 'task2', 'task1']

# RPUSH - 从右侧（尾部）插入
r.rpush('tasks', 'task4')
# 列表现在是: ['task3', 'task2', 'task1', 'task4']

# LRANGE - 获取范围内的元素
print(r.lrange('tasks', 0, -1))
# 输出: ['task3', 'task2', 'task1', 'task4']
# 注意: -1 表示最后一个元素

# LLEN - 获取列表长度
print(r.llen('tasks'))  # 输出: 4

# LPOP - 从左侧弹出元素
task = r.lpop('tasks')
print(f'处理任务: {task}')  # 输出: 处理任务: task3
print(r.lrange('tasks', 0, -1))  # 输出: ['task2', 'task1', 'task4']

# RPOP - 从右侧弹出元素
task = r.rpop('tasks')
print(f'处理任务: {task}')  # 输出: 处理任务: task4

# LINDEX - 获取指定位置的元素
print(r.lindex('tasks', 0))  # 输出: task2

# LSET - 设置指定位置的值
r.lset('tasks', 0, 'new_task')
print(r.lrange('tasks', 0, -1))  # 输出: ['new_task', 'task1']

# LTRIM - 修剪列表，只保留指定范围
r.lpush('logs', *[f'log{i}' for i in range(10)])
r.ltrim('logs', 0, 4)  # 只保留前 5 个
print(r.lrange('logs', 0, -1))  # 输出: ['log9', 'log8', 'log7', 'log6', 'log5']
```

### 8.3 实际应用：消息队列

```python
import redis
import time

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

def producer(queue_name, message):
    """生产者：发送消息到队列"""
    r.lpush(queue_name, message)
    print(f'发送消息: {message}')

def consumer(queue_name):
    """消费者：从队列获取消息"""
    # BRPOP 是阻塞式弹出，如果队列为空会等待
    result = r.brpop(queue_name, timeout=5)
    if result:
        _, message = result
        print(f'收到消息: {message}')
        return message
    else:
        print('超时，没有新消息')
        return None

# 使用示例
producer('task_queue', '处理订单 #1001')
producer('task_queue', '发送邮件通知')
producer('task_queue', '更新库存')

# 消费消息
while True:
    msg = consumer('task_queue')
    if msg is None:
        break
```

---

## 第 9 章：集合（Set）

### 9.1 概述

Redis Set 是一个**无序的、不重复的字符串集合**。类似于 Python 的 `set`。

**典型应用场景：**
- 标签系统
- 好友关系
- 去重统计

### 9.2 常用命令

```python
import redis
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# SADD - 添加成员
r.sadd('tags:article:1', 'Python', 'Redis', '数据库')
r.sadd('tags:article:1', 'Python')  # 重复添加会被忽略
print(r.smembers('tags:article:1'))
# 输出: {'Python', 'Redis', '数据库'}

# SMEMBERS - 获取所有成员
print(r.smembers('tags:article:1'))

# SISMEMBER - 判断成员是否存在
print(r.sismember('tags:article:1', 'Python'))   # 输出: True
print(r.sismember('tags:article:1', 'Java'))     # 输出: False

# SCARD - 获取成员数量
print(r.scard('tags:article:1'))  # 输出: 3

# SREM - 移除成员
r.srem('tags:article:1', '数据库')
print(r.smembers('tags:article:1'))  # 输出: {'Python', 'Redis'}

# SPOP - 随机弹出一个成员
member = r.spop('tags:article:1')
print(f'弹出: {member}')

# SRANDMEMBER - 随机获取成员（不删除）
print(r.srandmember('tags:article:1'))
```

### 9.3 集合运算

```python
import redis
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# 准备数据
r.sadd('user:A:hobbies', '读书', '游泳', '编程', '音乐')
r.sadd('user:B:hobbies', '游泳', '跑步', '编程', '绘画')

# SINTER - 交集（共同爱好）
common = r.sinter('user:A:hobbies', 'user:B:hobbies')
print(f'共同爱好: {common}')  # 输出: {'游泳', '编程'}

# SUNION - 并集（所有爱好）
all_hobbies = r.sunion('user:A:hobbies', 'user:B:hobbies')
print(f'所有爱好: {all_hobbies}')
# 输出: {'读书', '游泳', '编程', '音乐', '跑步', '绘画'}

# SDIFF - 差集（A 有但 B 没有的）
diff = r.sdiff('user:A:hobbies', 'user:B:hobbies')
print(f'A 独有: {diff}')  # 输出: {'读书', '音乐'}

# SINTERSTORE - 交集结果存储到新集合
r.sinterstore('common_hobbies', 'user:A:hobbies', 'user:B:hobbies')
print(r.smembers('common_hobbies'))  # 输出: {'游泳', '编程'}
```

### 9.4 实际应用：共同好友

```python
import redis
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# 添加好友
r.sadd('user:alice:friends', 'bob', 'charlie', 'david')
r.sadd('user:bob:friends', 'alice', 'charlie', 'eve')

# 查找共同好友
mutual = r.sinter('user:alice:friends', 'user:bob:friends')
print(f'Alice 和 Bob 的共同好友: {mutual}')  # 输出: {'charlie'}
```

---

## 第 10 章：有序集合（Sorted Set）

### 10.1 概述

Sorted Set（ZSet）是 Set 的升级版，每个成员都关联一个**分数（score）**。成员按分数**自动排序**。

**典型应用场景：**
- 排行榜
- 优先级队列
- 带权重的任务调度

### 10.2 常用命令

```python
import redis
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# ZADD - 添加成员和分数
r.zadd('leaderboard', {'Alice': 100, 'Bob': 85, 'Charlie': 92})

# 也可以一次添加一个
r.zadd('leaderboard', {'David': 78})

# ZRANGE - 按分数从低到高获取
print(r.zrange('leaderboard', 0, -1))
# 输出: ['David', 'Bob', 'Charlie', 'Alice']

# ZRANGE 带分数
print(r.zrange('leaderboard', 0, -1, withscores=True))
# 输出: [('David', 78.0), ('Bob', 85.0), ('Charlie', 92.0), ('Alice', 100.0)]

# ZREVRANGE - 按分数从高到低获取（排行榜常用）
print(r.zrevrange('leaderboard', 0, -1, withscores=True))
# 输出: [('Alice', 100.0), ('Charlie', 92.0), ('Bob', 85.0), ('David', 78.0)]

# ZSCORE - 获取成员的分数
print(r.zscore('leaderboard', 'Alice'))  # 输出: 100.0

# ZRANK - 获取成员的排名（从 0 开始，分数低排名靠前）
print(r.zrank('leaderboard', 'Bob'))  # 输出: 1

# ZREVRANK - 获取成员的排名（分数高排名靠前）
print(r.zrevrank('leaderboard', 'Alice'))  # 输出: 0

# ZCARD - 获取成员数量
print(r.zcard('leaderboard'))  # 输出: 4

# ZINCRBY - 增加成员的分数
r.zincrby('leaderboard', 10, 'Bob')
print(r.zscore('leaderboard', 'Bob'))  # 输出: 95.0

# ZREM - 移除成员
r.zrem('leaderboard', 'David')
print(r.zrevrange('leaderboard', 0, -1, withscores=True))
# 输出: [('Alice', 100.0), ('Charlie', 92.0), ('Bob', 95.0)]

# ZRANGEBYSCORE - 按分数范围获取
r.zadd('scores', {'A': 60, 'B': 75, 'C': 85, 'D': 90, 'E': 95})
print(r.zrangebyscore('scores', 70, 90))
# 输出: ['B', 'C', 'D']
```

### 10.3 实际应用：实时排行榜

```python
import redis
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

class Leaderboard:
    def __init__(self, name):
        self.name = name
        self.r = redis.Redis(host='localhost', port=6379, decode_responses=True)

    def add_score(self, user, score):
        """添加或更新用户分数"""
        self.r.zadd(self.name, {user: score})

    def get_rank(self, user):
        """获取用户排名（从 1 开始）"""
        rank = self.r.zrevrank(self.name, user)
        return rank + 1 if rank is not None else None

    def get_score(self, user):
        """获取用户分数"""
        return self.r.zscore(self.name, user)

    def get_top_n(self, n=10):
        """获取前 N 名"""
        return self.r.zrevrange(self.name, 0, n - 1, withscores=True)

# 使用示例
lb = Leaderboard('game:rank')

# 添加分数
lb.add_score('Alice', 1500)
lb.add_score('Bob', 1200)
lb.add_score('Charlie', 1800)
lb.add_score('David', 900)

# 查看排行榜
print('=== 排行榜 ===')
for rank, (user, score) in enumerate(lb.get_top_n(5), 1):
    print(f'第{rank}名: {user} - {score}分')

# 输出:
# 第1名: Charlie - 1800.0分
# 第2名: Alice - 1500.0分
# 第3名: Bob - 1200.0分
# 第4名: David - 900.0分

# 查询个人排名
print(f'\nAlice 的排名: 第{lb.get_rank("Alice")}名')
```

---

## 第 11 章：键的过期与持久化

### 11.1 过期命令

```python
import redis
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# SET 时指定过期时间
r.set('temp_key', 'value', ex=60)  # 60 秒后过期
r.set('temp_key_ms', 'value', px=60000)  # 60000 毫秒后过期

# 使用 EXPIRE 设置过期时间
r.set('my_key', 'data')
r.expire('my_key', 3600)  # 1 小时后过期

# 使用 EXPIREAT 设置具体时间
import time
r.expireat('my_key', int(time.time()) + 3600)

# 查看剩余时间
print(r.ttl('my_key'))    # 秒
print(r.pttl('my_key'))   # 毫秒

# 移除过期时间
r.persist('my_key')

# 检查键是否存在
print(r.exists('my_key'))  # 1 表示存在
```

### 11.2 过期策略

Redis 使用**惰性删除 + 定期删除**的策略：

- **惰性删除**：访问键时发现已过期则删除
- **定期删除**：后台定期扫描并删除过期键

这意味着过期键不一定立即被删除，但不会影响正确性。

---

# 高级篇：进阶特性

## 第 12 章：发布与订阅（Pub/Sub）

### 12.1 概述

Pub/Sub 是一种**消息通信模式**：发布者（Publisher）发送消息到频道（Channel），订阅者（Subscriber）接收该频道的消息。

**特点：**
- 消息不会持久化，订阅者离线时会丢失消息
- 适合实时通知、聊天系统等场景

### 12.2 基本用法

```python
import redis
import threading
import time

# 发布者
def publisher():
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    time.sleep(1)  # 等待订阅者启动
    r.publish('news', '第一条新闻：Redis 发布新版本')
    time.sleep(1)
    r.publish('news', '第二条新闻：Python 3.12 发布')
    time.sleep(1)
    r.publish('news', 'EXIT')  # 发送退出信号

# 订阅者
def subscriber():
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    pubsub = r.pubsub()
    pubsub.subscribe('news')

    print('等待消息...')
    for message in pubsub.listen():
        if message['type'] == 'message':
            data = message['data']
            print(f'收到: {data}')
            if data == 'EXIT':
                break

    pubsub.unsubscribe('news')
    print('订阅结束')

# 运行
t1 = threading.Thread(target=publisher)
t2 = threading.Thread(target=subscriber)
t2.start()
t1.start()
t1.join()
t2.join()
```

### 12.3 模式订阅

```python
# 订阅所有以 "user:" 开头的频道
pubsub.psubscribe('user:*')

# 发布到特定频道
r.publish('user:1001', '用户 1001 上线')
r.publish('user:1002', '用户 1002 上线')
```

---

## 第 13 章：事务（Transaction）

### 13.1 概述

Redis 事务通过 `MULTI`、`EXEC`、`DISCARD` 命令实现。它允许将多个命令打包，一次性执行。

**特点：**
- 事务中的命令按顺序执行，不会被中断
- **不支持回滚**（这是与数据库事务的重要区别）
- 如果某个命令执行失败，其他命令仍会继续执行

### 13.2 基本用法

```python
import redis
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# 方式 1：使用 pipeline（推荐）
pipe = r.pipeline()
pipe.multi()
pipe.set('user:1:name', '张三')
pipe.set('user:1:age', 25)
pipe.incr('user:1:login_count')
results = pipe.execute()
print(results)  # 输出: [True, True, 1]

# 方式 2：使用 transaction 上下文管理器
with r.pipeline() as pipe:
    pipe.multi()
    pipe.set('key1', 'value1')
    pipe.set('key2', 'value2')
    results = pipe.execute()
    print(results)  # 输出: [True, True]
```

### 13.3 WATCH 乐观锁

```python
import redis

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# 使用 WATCH 实现乐观锁
with r.pipeline() as pipe:
    while True:
        try:
            # 监视键，如果其他客户端修改了它，EXEC 会失败
            pipe.watch('balance')

            # 获取当前值
            balance = int(r.get('balance') or 1000)

            # 开始事务
            pipe.multi()
            pipe.set('balance', balance - 100)

            # 执行事务
            pipe.execute()
            print('扣款成功')
            break
        except redis.WatchError:
            # 如果键被其他客户端修改，重试
            print('数据被修改，重试中...')
            continue
```

---

## 第 14 章：Lua 脚本

### 14.1 概述

Redis 支持执行 Lua 脚本，可以将多个命令组合成一个**原子操作**。脚本执行期间不会被其他命令打断。

**优势：**
- 减少网络往返
- 保证原子性
- 可以包含复杂逻辑

### 14.2 基本用法

```python
import redis
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# 方式 1：直接执行 Lua 脚本
lua_script = """
local current = redis.call('GET', KEYS[1])
if current then
    return tonumber(current) + tonumber(ARGV[1])
else
    return ARGV[1]
end
"""
result = r.eval(lua_script, 1, 'counter', 10)
print(result)  # 输出: 10

# 方式 2：注册脚本（推荐，更高效）
# register_script 会缓存脚本的 SHA1，后续执行只需传 SHA1
script = r.register_script(lua_script)
result = script(keys=['counter'], args=[5])
print(result)  # 输出: 15

# 再次执行
result = script(keys=['counter'], args=[3])
print(result)  # 输出: 18
```

**参数说明：**
- `KEYS[1]`：第一个键参数
- `ARGV[1]`：第一个值参数
- `eval(script, numkeys, key1, key2, ..., arg1, arg2, ...)`：`numkeys` 是键的数量

### 14.3 实际应用：限流器

```python
import redis
import time

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Lua 脚本实现滑动窗口限流
rate_limit_script = """
local key = KEYS[1]
local limit = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local current = tonumber(redis.call('GET', key) or "0")

if current + 1 > limit then
    return 0  -- 超过限制
else
    redis.call('INCR', key)
    if current == 0 then
        redis.call('EXPIRE', key, window)
    end
    return 1  -- 允许通过
end
"""

script = r.register_script(rate_limit_script)

def check_rate_limit(user_id, limit=5, window=60):
    """检查用户是否在限流范围内"""
    key = f'rate_limit:{user_id}'
    result = script(keys=[key], args=[limit, window])
    return result == 1

# 测试
for i in range(7):
    allowed = check_rate_limit('user:1', limit=5, window=60)
    print(f'请求 {i+1}: {"允许" if allowed else "拒绝"}')

# 输出:
# 请求 1: 允许
# 请求 2: 允许
# 请求 3: 允许
# 请求 4: 允许
# 请求 5: 允许
# 请求 6: 拒绝
# 请求 7: 拒绝
```

---

## 第 15 章：管道（Pipeline）

### 15.1 概述

Pipeline 允许**一次性发送多个命令**到 Redis，然后一次性接收所有结果。这可以显著减少网络延迟。

**为什么需要 Pipeline？**

```
不使用 Pipeline：
客户端 → 命令1 → 等待响应 → 命令2 → 等待响应 → 命令3 → 等待响应

使用 Pipeline：
客户端 → [命令1, 命令2, 命令3] → 等待所有响应
```

### 15.2 基本用法

```python
import redis
import time

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# 方式 1：普通方式（慢）
start = time.time()
for i in range(1000):
    r.set(f'key:{i}', f'value:{i}')
print(f'普通方式耗时: {time.time() - start:.4f}秒')

# 方式 2：使用 Pipeline（快）
start = time.time()
pipe = r.pipeline()
for i in range(1000):
    pipe.set(f'key2:{i}', f'value:{i}')
pipe.execute()
print(f'Pipeline 方式耗时: {time.time() - start:.4f}秒')
```

### 15.3 批量操作

```python
import redis
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# 批量设置
pipe = r.pipeline()
pipe.set('user:1:name', '张三')
pipe.set('user:1:age', 25)
pipe.set('user:1:email', 'zhangsan@example.com')
pipe.hset('user:2', mapping={'name': '李四', 'age': 30})
pipe.lpush('tasks', 'task1', 'task2', 'task3')
results = pipe.execute()
print(results)  # 输出: [True, True, True, True, 3]

# 批量获取
pipe = r.pipeline()
pipe.get('user:1:name')
pipe.get('user:1:age')
pipe.hgetall('user:2')
results = pipe.execute()
print(results)  # 输出: ['张三', '25', {'name': '李四', 'age': '30'}]
```

---

## 第 16 章：Redis JSON

### 16.1 概述

RedisJSON 是 Redis 的一个模块，允许在 Redis 中原生存储和操作 JSON 文档。

**安装：**
```bash
# 使用 Redis Stack（包含 RedisJSON）
docker run -d --name redis-stack -p 6379:6379 redis/redis-stack:latest
```

### 16.2 基本用法

```python
import redis
from redis.commands.json.path import Path

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# JSON.SET - 设置 JSON 数据
r.json().set('user:1', Path.root_path(), {
    'name': '张三',
    'age': 25,
    'address': {
        'city': '北京',
        'district': '朝阳区'
    },
    'hobbies': ['读书', '游泳', '编程']
})

# JSON.GET - 获取 JSON 数据
user = r.json().get('user:1')
print(user)
# 输出: {'name': '张三', 'age': 25, 'address': {'city': '北京', 'district': '朝阳区'}, 'hobbies': ['读书', '游泳', '编程']}

# 获取特定路径
city = r.json().get('user:1', '$.address.city')
print(city)  # 输出: ['北京']

name = r.json().get('user:1', '$.name')
print(name)  # 输出: ['张三']

# JSON.ARRAPPEND - 追加数组元素
r.json().arrappend('user:1', '$.hobbies', '音乐')
print(r.json().get('user:1', '$.hobbies'))
# 输出: [['读书', '游泳', '编程', '音乐']]

# JSON.NUMINCRBY - 数字字段自增
r.json().numincrby('user:1', '$.age', 1)
print(r.json().get('user:1', '$.age'))  # 输出: [26]

# JSON.DEL - 删除字段
r.json().del_('user:1', '$.address.district')
print(r.json().get('user:1'))
```

---

## 第 17 章：Redis Search 全文搜索

### 17.1 概述

RediSearch 是 Redis 的全文搜索和向量数据库模块。它支持：
- 全文搜索
- 向量相似度搜索
- 聚合查询

### 17.2 创建索引

```python
import redis
from redis.commands.search.field import TextField, NumericField, TagField
from redis.commands.search.index_definition import IndexDefinition, IndexType
from redis.commands.search.query import Query

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# 创建索引
r.ft('idx:products').create_index(
    [
        TextField('$.name', as_name='name'),
        TextField('$.description', as_name='description'),
        NumericField('$.price', as_name='price'),
        TagField('$.category', as_name='category'),
    ],
    definition=IndexDefinition(prefix=['product:'], index_type=IndexType.JSON),
)

# 添加数据
products = [
    {'name': 'iPhone 15', 'description': 'Apple 最新智能手机', 'price': 5999, 'category': '手机'},
    {'name': 'MacBook Pro', 'description': 'Apple 专业笔记本电脑', 'price': 14999, 'category': '电脑'},
    {'name': 'AirPods Pro', 'description': 'Apple 无线降噪耳机', 'price': 1999, 'category': '耳机'},
]

for i, product in enumerate(products):
    r.json().set(f'product:{i}', '$', product)

# 搜索
# 1. 全文搜索
res = r.ft('idx:products').search(Query('Apple'))
print(f'找到 {res.total} 个结果')
for doc in res.docs:
    print(doc.json)

# 2. 按价格范围搜索
res = r.ft('idx:products').search(Query('@price:[2000 10000]'))
print(f'价格在 2000-10000 之间的商品: {res.total}个')

# 3. 按类别搜索
res = r.ft('idx:products').search(Query('@category:{手机}'))
print(f'手机类商品: {res.total}个')

# 4. 组合搜索
res = r.ft('idx:products').search(Query('手机 @price:[3000 8000]'))
print(f'3000-8000 元的手机: {res.total}个')
```

---

## 第 18 章：持久化机制

### 18.1 RDB（快照）

RDB 是 Redis 默认的持久化方式。它会定期将内存中的数据快照保存到磁盘。

**配置（redis.conf）：**
```
save 900 1     # 900 秒内至少 1 个键变化，则触发快照
save 300 10    # 300 秒内至少 10 个键变化，则触发快照
save 60 10000  # 60 秒内至少 10000 个键变化，则触发快照

dbfilename dump.rdb  # 快照文件名
dir ./               # 快照保存目录
```

**特点：**
- 文件紧凑，适合备份
- 恢复速度快
- 可能丢失最后一次快照后的数据

### 18.2 AOF（追加日志）

AOF 记录每个写操作，重启时重新执行这些操作来恢复数据。

**配置：**
```
appendonly yes
appendfilename "appendonly.aof"
appendfsync everysec  # 每秒同步一次（推荐）
```

**appendfsync 选项：**
- `always`：每次写操作都同步，最安全但最慢
- `everysec`：每秒同步一次，推荐
- `no`：由操作系统决定何时同步，最快但最不安全

**特点：**
- 数据更安全，最多丢失 1 秒数据
- 文件比 RDB 大
- 恢复速度比 RDB 慢

### 18.3 混合持久化（推荐）

Redis 4.0+ 支持混合持久化，结合 RDB 和 AOF 的优点：

```
aof-use-rdb-preamble yes
```

这样 AOF 文件开头是 RDB 格式的全量数据，后面是 AOF 格式的增量日志。

---

## 第 19 章：在 LangChain 项目中使用 Redis

### 19.1 作为消息历史存储

```python
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage

# 使用 Redis 存储聊天历史
history = RedisChatMessageHistory(
    session_id='user:123',
    url='redis://localhost:6379/0'
)

# 添加消息
history.add_user_message("你好")
history.add_ai_message("你好！有什么可以帮助你的？")

# 获取历史消息
print(history.messages)
```

### 19.2 作为缓存

```python
from langchain_community.cache import RedisCache
import redis
from langchain_core.globals import set_llm_cache

# 设置 Redis 缓存
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
set_llm_cache(RedisCache(redis_=redis_client))

# 之后调用 LLM 时，相同的输入会被缓存
# 第二次调用相同输入时会直接返回缓存结果，不再请求 API
```

### 19.3 作为向量存储

```python
from langchain_community.vectorstores import Redis
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings()

# 创建 Redis 向量存储
vectorstore = Redis.from_texts(
    texts=["文档内容 1", "文档内容 2", "文档内容 3"],
    embedding=embeddings,
    redis_url="redis://localhost:6379",
    index_name="my_docs"
)

# 相似度搜索
results = vectorstore.similarity_search("查询内容", k=2)
for doc in results:
    print(doc.page_content)
```

### 19.4 作为 Agent 的记忆

```python
import redis
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# 存储用户偏好
r.hset('user:preferences', mapping={
    'language': '中文',
    'style': '简洁',
    'topic': '技术'
})

# 在动态提示词中使用
def get_user_context(user_id):
    prefs = r.hgetall(f'user:{user_id}:preferences')
    return prefs

# 结合 @dynamic_prompt 使用
# 参考 test21_agent.py 中的用法
```

---

## 附录：常用命令速查表

### 键操作
| 命令 | 说明 | 示例 |
|------|------|------|
| `SET` | 设置值 | `SET key value` |
| `GET` | 获取值 | `GET key` |
| `DEL` | 删除 | `DEL key` |
| `EXISTS` | 检查是否存在 | `EXISTS key` |
| `EXPIRE` | 设置过期时间 | `EXPIRE key seconds` |
| `TTL` | 查看剩余时间 | `TTL key` |
| `KEYS` | 匹配键 | `KEYS pattern` |
| `TYPE` | 查看类型 | `TYPE key` |

### 字符串
| 命令 | 说明 |
|------|------|
| `MSET` | 批量设置 |
| `MGET` | 批量获取 |
| `INCR` | 自增 1 |
| `INCRBY` | 自增 N |
| `DECR` | 自减 1 |
| `APPEND` | 追加 |

### 哈希
| 命令 | 说明 |
|------|------|
| `HSET` | 设置字段 |
| `HGET` | 获取字段 |
| `HGETALL` | 获取所有字段 |
| `HDEL` | 删除字段 |
| `HINCRBY` | 字段自增 |
| `HEXISTS` | 字段是否存在 |

### 列表
| 命令 | 说明 |
|------|------|
| `LPUSH` | 左侧插入 |
| `RPUSH` | 右侧插入 |
| `LPOP` | 左侧弹出 |
| `RPOP` | 右侧弹出 |
| `LRANGE` | 范围查询 |
| `LLEN` | 长度 |

### 集合
| 命令 | 说明 |
|------|------|
| `SADD` | 添加成员 |
| `SMEMBERS` | 所有成员 |
| `SISMEMBER` | 成员是否存在 |
| `SINTER` | 交集 |
| `SUNION` | 并集 |
| `SDIFF` | 差集 |

### 有序集合
| 命令 | 说明 |
|------|------|
| `ZADD` | 添加成员和分数 |
| `ZRANGE` | 范围查询（低到高） |
| `ZREVRANGE` | 范围查询（高到低） |
| `ZSCORE` | 获取分数 |
| `ZINCRBY` | 分数自增 |
| `ZRANK` | 获取排名 |

---

## 参考资源

- **Redis 官方文档**：https://redis.io/docs/
- **Redis 命令参考**：https://redis.io/commands/
- **redis-py 文档**：https://redis.readthedocs.io/
- **Redis 教程**：https://learn.redis.com/
- **Redis 大学**：https://university.redis.com/
