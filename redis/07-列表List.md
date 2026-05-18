# 第 7 章：列表（List）——消息队列

> 本章目标：学会用 List 实现队列、栈、最新消息等功能。

---

## 一、列表是什么？

Redis List 是一个**有序的元素集合**，元素可以重复。

想象一列火车：

```
车头 ← [车厢3] [车厢2] [车厢1] → 车尾
```

- 你可以从**车头**加车厢，也可以从**车尾**加车厢
- 你可以从**车头**卸车厢，也可以从**车尾**卸车厢

这就是 List 的核心操作：**两端都可以插入和弹出**。

---

## 二、基本操作

### LPUSH：从左侧（头部）插入

```
127.0.0.1:6379> LPUSH tasks "task1"
(integer) 1

127.0.0.1:6379> LPUSH tasks "task2"
(integer) 2

127.0.0.1:6379> LPUSH tasks "task3"
(integer) 3
```

**解释：**
- `LPUSH`：Left Push，从左边推入
- 每次插入到列表头部
- 返回插入后列表的长度

**列表现在的状态：**

```
[task3] → [task2] → [task1]
 ↑ 头部              ↑ 尾部
```

### RPUSH：从右侧（尾部）插入

```
127.0.0.1:6379> RPUSH tasks "task4"
(integer) 4
```

**列表现在的状态：**

```
[task3] → [task2] → [task1] → [task4]
 ↑ 头部                          ↑ 尾部
```

### LRANGE：查看列表内容

```
127.0.0.1:6379> LRANGE tasks 0 -1
1) "task3"
2) "task2"
3) "task1"
4) "task4"
```

**语法说明：**
- `LRANGE key start stop`：获取从 start 到 stop 范围的元素
- `0` 表示第一个元素
- `-1` 表示最后一个元素
- `0 -1` 表示获取所有元素

### 获取部分元素

```
# 获取前 2 个
127.0.0.1:6379> LRANGE tasks 0 1
1) "task3"
2) "task2"

# 获取最后 2 个
127.0.0.1:6379> LRANGE tasks -2 -1
1) "task1"
2) "task4"
```

---

## 三、弹出元素

### LPOP：从左侧弹出

```
127.0.0.1:6379> LPOP tasks
"task3"

127.0.0.1:6379> LRANGE tasks 0 -1
1) "task2"
2) "task1"
3) "task4"
```

**解释：**
- `LPOP`：Left Pop，从左边弹出
- 返回并删除头部元素

### RPOP：从右侧弹出

```
127.0.0.1:6379> RPOP tasks
"task4"

127.0.0.1:6379> LRANGE tasks 0 -1
1) "task2"
2) "task1"
```

---

## 四、队列和栈

### 用 List 实现队列（FIFO：先进先出）

队列就像排队买票，**先来的先服务**。

```
入队：RPUSH（从尾部加入）
出队：LPOP（从头部取出）
```

```
127.0.0.1:6379> RPUSH queue "用户A" "用户B" "用户C"
(integer) 3

127.0.0.1:6379> LPOP queue
"用户A"

127.0.0.1:6379> LPOP queue
"用户B"
```

### 用 List 实现栈（LIFO：后进先出）

栈就像叠盘子，**最后放的先取**。

```
入栈：LPUSH（从头部放入）
出栈：LPOP（从头部取出）
```

```
127.0.0.1:6379> LPUSH stack "盘子1"
(integer) 1

127.0.0.1:6379> LPUSH stack "盘子2"
(integer) 2

127.0.0.1:6379> LPUSH stack "盘子3"
(integer) 3

127.0.0.1:6379> LPOP stack
"盘子3"
```

---

## 五、其他常用命令

### LLEN：获取列表长度

```
127.0.0.1:6379> LLEN tasks
(integer) 2
```

### LINDEX：获取指定位置的元素

```
127.0.0.1:6379> LRANGE tasks 0 -1
1) "task2"
2) "task1"

127.0.0.1:6379> LINDEX tasks 0
"task2"

127.0.0.1:6379> LINDEX tasks 1
"task1"

127.0.0.1:6379> LINDEX tasks -1
"task1"
```

### LSET：修改指定位置的元素

```
127.0.0.1:6379> LSET tasks 0 "new_task"
OK

127.0.0.1:6379> LRANGE tasks 0 -1
1) "new_task"
2) "task1"
```

### LTRIM：修剪列表

```
127.0.0.1:6379> LPUSH logs "log1" "log2" "log3" "log4" "log5"
(integer) 5

127.0.0.1:6379> LTRIM logs 0 2
OK

127.0.0.1:6379> LRANGE logs 0 -1
1) "log5"
2) "log4"
3) "log3"
```

**解释：**
- `LTRIM key start stop`：只保留 start 到 stop 范围的元素，其余删除
- 常用于**限制列表长度**，比如只保留最新的 100 条日志

---

## 六、阻塞操作：BLPOP 和 BRPOP

这是 List 最强大的功能之一。

### 什么是阻塞？

普通 `LPOP` 如果列表为空，会立即返回 `nil`。

但 `BLPOP` 如果列表为空，会**等待**，直到有元素被推入。

```
127.0.0.1:6379> BLPOP queue 30
```

**解释：**
- `BLPOP`：Blocking Left Pop，阻塞式弹出
- `30`：最多等待 30 秒
- 如果 30 秒内有元素推入，立即返回
- 如果 30 秒后还是没有元素，返回 `nil`

### 图示理解

```
消费者执行 BLPOP queue 30
        │
        │ 列表为空，等待中...
        │
        │ ← 生产者执行 RPUSH queue "新任务"
        │
        │ 立即返回 "新任务"
        ▼
    处理任务
```

---

## 七、Python 代码

```python
import redis

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# LPUSH：从左侧插入
r.lpush('tasks', 'task1')
r.lpush('tasks', 'task2')
r.lpush('tasks', 'task3')

# 查看列表
print(r.lrange('tasks', 0, -1))
# 输出: ['task3', 'task2', 'task1']

# RPUSH：从右侧插入
r.rpush('tasks', 'task4')
print(r.lrange('tasks', 0, -1))
# 输出: ['task3', 'task2', 'task1', 'task4']

# LPOP：从左侧弹出
task = r.lpop('tasks')
print(f'处理: {task}')  # 输出: 处理: task3

# RPOP：从右侧弹出
task = r.rpop('tasks')
print(f'处理: {task}')  # 输出: 处理: task4

# LLEN：长度
print(r.llen('tasks'))  # 输出: 2

# LINDEX：获取指定位置
print(r.lindex('tasks', 0))  # 输出: task2

# BLPOP：阻塞式弹出（等待 5 秒）
result = r.blpop('tasks', timeout=5)
if result:
    _, task = result
    print(f'阻塞获取: {task}')
else:
    print('超时，没有任务')
```

---

## 八、实战：消息队列系统

```python
import redis
import time
import threading

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

class MessageQueue:
    """消息队列"""

    def __init__(self, queue_name):
        self.queue_name = queue_name
        self.r = redis.Redis(host='localhost', port=6379, decode_responses=True)

    def publish(self, message):
        """发布消息"""
        self.r.rpush(self.queue_name, message)
        print(f'发布: {message}')

    def consume(self, timeout=10):
        """消费消息（阻塞等待）"""
        result = self.r.blpop(self.queue_name, timeout=timeout)
        if result:
            _, message = result
            print(f'消费: {message}')
            return message
        else:
            print('等待超时，没有新消息')
            return None

    def size(self):
        """查看队列中有多少消息"""
        return self.r.llen(self.queue_name)

# 使用示例
queue = MessageQueue('order_queue')

# 生产者：发布订单
queue.publish('订单 #1001')
queue.publish('订单 #1002')
queue.publish('订单 #1003')

print(f'队列中有 {queue.size()} 个待处理订单')

# 消费者：处理订单
while True:
    msg = queue.consume(timeout=2)
    if msg is None:
        break

# 输出:
# 发布: 订单 #1001
# 发布: 订单 #1002
# 发布: 订单 #1003
# 队列中有 3 个待处理订单
# 消费: 订单 #1001
# 消费: 订单 #1002
# 消费: 订单 #1003
# 等待超时，没有新消息
```

---

## 九、实战：最新消息列表

```python
import redis

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

class LatestNews:
    """最新消息列表（只保留最新 10 条）"""

    def __init__(self):
        self.r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        self.key = 'news:latest'
        self.max_len = 10

    def add_news(self, title):
        """添加新闻"""
        self.r.lpush(self.key, title)
        # 修剪，只保留最新 10 条
        self.r.ltrim(self.key, 0, self.max_len - 1)
        print(f'添加: {title}')

    def get_news(self, count=5):
        """获取最新 N 条新闻"""
        return self.r.lrange(self.key, 0, count - 1)

# 使用示例
news = LatestNews()

# 添加新闻
for i in range(1, 15):
    news.add_news(f'新闻标题 {i}')

# 查看最新 5 条
print('\n最新 5 条新闻:')
for i, title in enumerate(news.get_news(5), 1):
    print(f'{i}. {title}')

# 输出:
# 最新 5 条新闻:
# 1. 新闻标题 14
# 2. 新闻标题 13
# 3. 新闻标题 12
# 4. 新闻标题 11
# 5. 新闻标题 10
```

---

## 十、本章小结

### 你需要记住的命令

| 命令 | 作用 | 示例 |
|------|------|------|
| `LPUSH` | 左侧插入 | `LPUSH key value` |
| `RPUSH` | 右侧插入 | `RPUSH key value` |
| `LPOP` | 左侧弹出 | `LPOP key` |
| `RPOP` | 右侧弹出 | `RPOP key` |
| `LRANGE` | 范围查询 | `LRANGE key 0 -1` |
| `LLEN` | 长度 | `LLEN key` |
| `LINDEX` | 获取指定位置 | `LINDEX key 0` |
| `LTRIM` | 修剪 | `LTRIM key 0 9` |
| `BLPOP` | 阻塞弹出 | `BLPOP key 30` |

### 核心理解

1. List 是**双向链表**，两端操作都是 O(1) 速度
2. `LPUSH + LPOP` = 栈（后进先出）
3. `RPUSH + LPOP` = 队列（先进先出）
4. `BLPOP` 可以实现**实时等待**新消息

### 下章预告

下一章我们会学习**集合（Set）**，实现去重和集合运算。

---

> 💡 **动手练习**：
> 1. 用 List 实现一个待办事项列表
> 2. 用 BLPOP 实现一个简单的消息队列
> 3. 用 LTRIM 限制列表只保留最新 10 条记录
