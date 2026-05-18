# 第 9 章：有序集合（Sorted Set）——排行榜

> 本章目标：学会用 Sorted Set 实现排行榜、优先级队列等功能。

---

## 一、有序集合是什么？

有序集合（Sorted Set，简称 ZSet）是 Set 的升级版。

**普通 Set：**
```
{Alice, Bob, Charlie}  ← 无序
```

**Sorted Set：**
```
每个成员都有一个分数（score）
Alice: 100
Bob: 85
Charlie: 92

按分数自动排序:
Bob(85) → Charlie(92) → Alice(100)
```

**核心特点：**
1. 成员**不重复**（和 Set 一样）
2. 每个成员关联一个**分数（score）**
3. 成员按分数**自动排序**

---

## 二、基本操作

### ZADD：添加成员和分数

```
127.0.0.1:6379> ZADD leaderboard 100 "Alice" 85 "Bob" 92 "Charlie"
(integer) 3
```

**解释：**
- `ZADD`：Sorted Set Add
- 语法：`ZADD key score1 member1 score2 member2 ...`
- 返回添加的成员数量

**存储后的排序（从低到高）：**
```
Bob(85) → Charlie(92) → Alice(100)
```

### ZRANGE：按分数从低到高获取

```
127.0.0.1:6379> ZRANGE leaderboard 0 -1
1) "Bob"
2) "Charlie"
3) "Alice"
```

**带分数一起获取：**

```
127.0.0.1:6379> ZRANGE leaderboard 0 -1 WITHSCORES
1) "Bob"
2) "85"
3) "Charlie"
4) "92"
5) "Alice"
6) "100"
```

### ZREVRANGE：按分数从高到低获取

排行榜通常用这个命令：

```
127.0.0.1:6379> ZREVRANGE leaderboard 0 -1 WITHSCORES
1) "Alice"
2) "100"
3) "Charlie"
4) "92"
5) "Bob"
6) "85"
```

**解释：**
- `ZREVRANGE`：Reverse Range，反向范围（从高到低）
- 排行榜第 1 名就是索引 0

---

## 三、查询操作

### ZSCORE：获取成员的分数

```
127.0.0.1:6379> ZSCORE leaderboard "Alice"
"100"
```

### ZRANK：获取成员的排名（从低到高）

```
127.0.0.1:6379> ZRANK leaderboard "Bob"
(integer) 0

127.0.0.1:6379> ZRANK leaderboard "Alice"
(integer) 2
```

**注意：** 排名从 0 开始，分数越低排名越靠前。

### ZREVRANK：获取成员的排名（从高到低）

排行榜常用这个：

```
127.0.0.1:6379> ZREVRANK leaderboard "Alice"
(integer) 0

127.0.0.1:6379> ZREVRANK leaderboard "Charlie"
(integer) 1
```

排名从 0 开始，分数越高排名越靠前。

### ZCARD：获取成员数量

```
127.0.0.1:6379> ZCARD leaderboard
(integer) 3
```

---

## 四、更新操作

### ZINCRBY：增加成员的分数

```
127.0.0.1:6379> ZINCRBY leaderboard 10 "Bob"
"95"

127.0.0.1:6379> ZREVRANGE leaderboard 0 -1 WITHSCORES
1) "Alice"
2) "100"
3) "Bob"
4) "95"
5) "Charlie"
6) "92"
```

Bob 的分数从 85 增加到 95，排名也上升了。

### ZREM：移除成员

```
127.0.0.1:6379> ZREM leaderboard "Charlie"
(integer) 1
```

---

## 五、范围查询

### ZRANGEBYSCORE：按分数范围获取

```
127.0.0.1:6379> ZADD scores 60 "A" 75 "B" 85 "C" 90 "D" 95 "E"
(integer) 5

127.0.0.1:6379> ZRANGEBYSCORE scores 70 90
1) "B"
2) "C"
3) "D"
```

**解释：**
- `ZRANGEBYSCORE key min max`：获取分数在 min 到 max 之间的成员

### 带分数

```
127.0.0.1:6379> ZRANGEBYSCORE scores 70 90 WITHSCORES
1) "B"
2) "75"
3) "C"
4) "85"
5) "D"
6) "90"
```

### 限制数量

```
127.0.0.1:6379> ZRANGEBYSCORE scores 0 100 WITHSCORES LIMIT 0 2
1) "A"
2) "60"
3) "B"
4) "75"
```

**LIMIT offset count**：跳过 offset 个，取 count 个（类似分页）。

### 开区间和闭区间

```
# 闭区间 [70, 90]：包含 70 和 90
127.0.0.1:6379> ZRANGEBYSCORE scores 70 90

# 开区间 (70, 90)：不包含 70 和 90
127.0.0.1:6379> ZRANGEBYSCORE scores (70 (90

# 半开区间 [70, 90)：包含 70，不包含 90
127.0.0.1:6379> ZRANGEBYSCORE scores 70 (90
```

**说明：** 在数字前加 `(` 表示开区间（不包含该值）。

---

## 六、Python 代码

```python
import redis

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# ZADD：添加成员和分数
r.zadd('leaderboard', {'Alice': 100, 'Bob': 85, 'Charlie': 92})

# ZRANGE：从低到高
print(r.zrange('leaderboard', 0, -1))
# 输出: ['Bob', 'Charlie', 'Alice']

# ZRANGE 带分数
print(r.zrange('leaderboard', 0, -1, withscores=True))
# 输出: [('Bob', 85.0), ('Charlie', 92.0), ('Alice', 100.0)]

# ZREVRANGE：从高到低（排行榜）
print(r.zrevrange('leaderboard', 0, -1, withscores=True))
# 输出: [('Alice', 100.0), ('Charlie', 92.0), ('Bob', 85.0)]

# ZSCORE：获取分数
print(r.zscore('leaderboard', 'Alice'))  # 输出: 100.0

# ZREVRANK：获取排名（从高到低，0 开始）
print(r.zrevrank('leaderboard', 'Alice'))  # 输出: 0
print(r.zrevrank('leaderboard', 'Bob'))    # 输出: 2

# ZINCRBY：增加分数
r.zincrby('leaderboard', 10, 'Bob')
print(r.zscore('leaderboard', 'Bob'))  # 输出: 95.0

# ZCARD：成员数量
print(r.zcard('leaderboard'))  # 输出: 3

# ZREM：移除成员
r.zrem('leaderboard', 'Charlie')

# ZRANGEBYSCORE：按分数范围
r.zadd('scores', {'A': 60, 'B': 75, 'C': 85, 'D': 90, 'E': 95})
print(r.zrangebyscore('scores', 70, 90))
# 输出: ['B', 'C', 'D']
```

---

## 七、实战：游戏排行榜

```python
import redis

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

class Leaderboard:
    """游戏排行榜"""

    def __init__(self, name):
        self.name = name
        self.r = redis.Redis(host='localhost', port=6379, decode_responses=True)

    def add_score(self, user, score):
        """添加或更新用户分数"""
        self.r.zadd(self.name, {user: score})
        print(f'{user} 得分: {score}')

    def get_rank(self, user):
        """获取用户排名（从 1 开始）"""
        rank = self.r.zrevrank(self.name, user)
        if rank is None:
            return None
        return rank + 1  # 排名从 1 开始

    def get_score(self, user):
        """获取用户分数"""
        score = self.r.zscore(self.name, user)
        return score if score else 0

    def get_top_n(self, n=10):
        """获取前 N 名"""
        return self.r.zrevrange(self.name, 0, n - 1, withscores=True)

    def get_users_in_range(self, min_score, max_score):
        """获取分数范围内的用户"""
        return self.r.zrangebyscore(self.name, min_score, max_score, withscores=True)

    def increase_score(self, user, increment):
        """增加用户分数"""
        new_score = self.r.zincrby(self.name, increment, user)
        print(f'{user} 增加 {increment} 分，当前: {new_score}')
        return new_score

# 使用示例
lb = Leaderboard('game:rank')

# 添加分数
lb.add_score('Alice', 1500)
lb.add_score('Bob', 1200)
lb.add_score('Charlie', 1800)
lb.add_score('David', 900)
lb.add_score('Eve', 2000)

# 查看排行榜
print('\n=== 排行榜 TOP 5 ===')
for rank, (user, score) in enumerate(lb.get_top_n(5), 1):
    print(f'第{rank}名: {user} - {int(score)}分')

# 输出:
# === 排行榜 TOP 5 ===
# 第1名: Eve - 2000分
# 第2名: Charlie - 1800分
# 第3名: Alice - 1500分
# 第4名: Bob - 1200分
# 第5名: David - 900分

# 查询个人排名
print(f'\nAlice 的排名: 第{lb.get_rank("Alice")}名')
print(f'Alice 的分数: {lb.get_score("Alice")}分')

# 分数增加
lb.increase_score('Bob', 400)
print(f'\nBob 的新排名: 第{lb.get_rank("Bob")}名')

# 查看分数范围
print('\n分数在 1000-1600 之间的玩家:')
for user, score in lb.get_users_in_range(1000, 1600):
    print(f'  {user}: {int(score)}分')
```

---

## 八、实战：优先级任务队列

```python
import redis
import time

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

class PriorityTaskQueue:
    """优先级任务队列"""

    def __init__(self):
        self.r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        self.key = 'task:priority'

    def add_task(self, task, priority):
        """添加任务，优先级越高越先执行"""
        # 分数用负数，这样 ZPOPMIN 会先弹出分数高的
        self.r.zadd(self.key, {task: -priority})
        print(f'添加任务: {task} (优先级: {priority})')

    def get_next_task(self):
        """获取下一个要执行的任务"""
        result = self.r.zpopmin(self.key)
        if result:
            task, score = result[0]
            print(f'执行任务: {task} (优先级: {-score})')
            return task
        else:
            print('没有待执行的任务')
            return None

    def get_pending_tasks(self):
        """查看所有待执行的任务"""
        return self.r.zrange(self.key, 0, -1, withscores=True)

# 使用示例
queue = PriorityTaskQueue()

# 添加任务（数字越大优先级越高）
queue.add_task('修复线上 Bug', 10)
queue.add_task('更新文档', 3)
queue.add_task('代码审查', 7)
queue.add_task('部署新版本', 8)
queue.add_task('写单元测试', 5)

# 查看待执行任务
print('\n待执行任务:')
for task, score in queue.get_pending_tasks():
    print(f'  {task} (优先级: {-int(score)})')

# 按优先级执行
print('\n开始执行:')
while True:
    task = queue.get_next_task()
    if task is None:
        break
    time.sleep(0.5)  # 模拟执行时间

# 输出:
# 添加任务: 修复线上 Bug (优先级: 10)
# 添加任务: 更新文档 (优先级: 3)
# 添加任务: 代码审查 (优先级: 7)
# 添加任务: 部署新版本 (优先级: 8)
# 添加任务: 写单元测试 (优先级: 5)
#
# 待执行任务:
#   修复线上 Bug (优先级: 10)
#   部署新版本 (优先级: 8)
#   代码审查 (优先级: 7)
#   写单元测试 (优先级: 5)
#   更新文档 (优先级: 3)
#
# 开始执行:
# 执行任务: 修复线上 Bug (优先级: 10)
# 执行任务: 部署新版本 (优先级: 8)
# 执行任务: 代码审查 (优先级: 7)
# 执行任务: 写单元测试 (优先级: 5)
# 执行任务: 更新文档 (优先级: 3)
# 没有待执行的任务
```

---

## 九、本章小结

### 你需要记住的命令

| 命令 | 作用 | 示例 |
|------|------|------|
| `ZADD` | 添加成员和分数 | `ZADD key score member` |
| `ZRANGE` | 从低到高获取 | `ZRANGE key 0 -1` |
| `ZREVRANGE` | 从高到低获取 | `ZREVRANGE key 0 -1` |
| `ZSCORE` | 获取分数 | `ZSCORE key member` |
| `ZREVRANK` | 获取排名 | `ZREVRANK key member` |
| `ZINCRBY` | 分数自增 | `ZINCRBY key 10 member` |
| `ZCARD` | 成员数量 | `ZCARD key` |
| `ZREM` | 移除成员 | `ZREM key member` |
| `ZRANGEBYSCORE` | 按分数范围获取 | `ZRANGEBYSCORE key min max` |

### 核心理解

1. Sorted Set = Set + 分数（score）
2. 成员按分数**自动排序**
3. 最适合的场景：**排行榜**、**优先级队列**

### 下章预告

下一章我们会学习**键的过期与持久化**，了解如何让数据自动过期以及如何保存数据。

---

> 💡 **动手练习**：
> 1. 用 ZSet 实现一个文章热度排行榜
> 2. 用 ZINCRBY 实现点赞功能并实时更新排名
> 3. 用 ZRANGEBYSCORE 查询分数在某个范围内的用户
