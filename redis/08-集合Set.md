# 第 8 章：集合（Set）——去重与集合运算

> 本章目标：学会用 Set 实现去重、标签系统、好友关系等功能。

---

## 一、集合是什么？

Redis Set 是一个**无序的、不重复的元素集合**。

用 Python 来类比：

```python
# Python 的 set
s = {'Python', 'Redis', '数据库'}
s.add('Python')  # 重复添加，会被忽略
print(s)  # 输出: {'Python', 'Redis', '数据库'}
```

**Set 的两个核心特点：**
1. **无序**：元素没有固定顺序
2. **不重复**：同一个元素只能存在一次

---

## 二、基本操作

### SADD：添加成员

```
127.0.0.1:6379> SADD tags:article:1 "Python" "Redis" "数据库"
(integer) 3
```

**解释：**
- `SADD`：Set Add，添加成员
- 可以一次添加多个
- 返回实际添加的数量（重复的不会计入）

```
127.0.0.1:6379> SADD tags:article:1 "Python"
(integer) 0
```

返回 `0`，因为 "Python" 已经存在，没有新成员被添加。

### SMEMBERS：获取所有成员

```
127.0.0.1:6379> SMEMBERS tags:article:1
1) "Python"
2) "Redis"
3) "数据库"
```

**注意：** 返回顺序可能和你添加的顺序不同，因为 Set 是无序的。

### SISMEMBER：判断成员是否存在

```
127.0.0.1:6379> SISMEMBER tags:article:1 "Python"
(integer) 1

127.0.0.1:6379> SISMEMBER tags:article:1 "Java"
(integer) 0
```

返回 `1` 表示存在，`0` 表示不存在。

### SCARD：获取成员数量

```
127.0.0.1:6379> SCARD tags:article:1
(integer) 3
```

### SREM：移除成员

```
127.0.0.1:6379> SREM tags:article:1 "数据库"
(integer) 1

127.0.0.1:6379> SMEMBERS tags:article:1
1) "Python"
2) "Redis"
```

---

## 三、随机操作

### SPOP：随机弹出一个成员

```
127.0.0.1:6379> SADD lottery "用户A" "用户B" "用户C" "用户D"
(integer) 4

127.0.0.1:6379> SPOP lottery
"用户C"

127.0.0.1:6379> SMEMBERS lottery
1) "用户A"
2) "用户B"
3) "用户D"
```

**解释：**
- `SPOP`：随机取出一个成员，并**从集合中删除**
- 适合抽奖场景

### SRANDMEMBER：随机获取成员（不删除）

```
127.0.0.1:6379> SRANDMEMBER lottery
"用户A"

127.0.0.1:6379> SMEMBERS lottery
1) "用户A"
2) "用户B"
3) "用户D"
```

**解释：**
- `SRANDMEMBER`：随机取出一个成员，但**不删除**
- 适合随机推荐场景

### 随机获取多个

```
127.0.0.1:6379> SRANDMEMBER lottery 2
1) "用户A"
2) "用户B"
```

---

## 四、集合运算（重点）

这是 Set 最强大的功能。

### 准备数据

```
127.0.0.1:6379> SADD user:A:hobbies "读书" "游泳" "编程" "音乐"
(integer) 4

127.0.0.1:6379> SADD user:B:hobbies "游泳" "跑步" "编程" "绘画"
(integer) 4
```

```
用户 A 的爱好: {读书, 游泳, 编程, 音乐}
用户 B 的爱好: {游泳, 跑步, 编程, 绘画}
```

### SINTER：交集（共同的）

```
127.0.0.1:6379> SINTER user:A:hobbies user:B:hobbies
1) "游泳"
2) "编程"
```

**交集** = 两个集合都有的元素 = 共同爱好

```
用户 A: {读书, 游泳, 编程, 音乐}
用户 B: {游泳, 跑步, 编程, 绘画}
交集:  {游泳, 编程}
```

### SUNION：并集（所有的）

```
127.0.0.1:6379> SUNION user:A:hobbies user:B:hobbies
1) "读书"
2) "游泳"
3) "编程"
4) "音乐"
5) "跑步"
6) "绘画"
```

**并集** = 两个集合的所有元素（去重）

### SDIFF：差集（A 有但 B 没有的）

```
127.0.0.1:6379> SDIFF user:A:hobbies user:B:hobbies
1) "读书"
2) "音乐"
```

**差集** = 在 A 中但不在 B 中的元素 = A 独有的爱好

```
127.0.0.1:6379> SDIFF user:B:hobbies user:A:hobbies
1) "跑步"
2) "绘画"
```

反过来就是 B 独有的爱好。

### 存储运算结果

```
127.0.0.1:6379> SINTERSTORE common_hobbies user:A:hobbies user:B:hobbies
(integer) 2

127.0.0.1:6379> SMEMBERS common_hobbies
1) "游泳"
2) "编程"
```

**解释：**
- `SINTERSTORE`：计算交集，并把结果存到一个新集合中
- 类似的还有 `SUNIONSTORE` 和 `SDIFFSTORE`

---

## 五、Python 代码

```python
import redis

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# SADD：添加成员
r.sadd('tags:article:1', 'Python', 'Redis', '数据库')

# SMEMBERS：获取所有成员
print(r.smembers('tags:article:1'))
# 输出: {'Python', 'Redis', '数据库'}

# SISMEMBER：判断是否存在
print(r.sismember('tags:article:1', 'Python'))  # 输出: True
print(r.sismember('tags:article:1', 'Java'))    # 输出: False

# SCARD：数量
print(r.scard('tags:article:1'))  # 输出: 3

# SREM：移除
r.srem('tags:article:1', '数据库')
print(r.smembers('tags:article:1'))
# 输出: {'Python', 'Redis'}

# SPOP：随机弹出
member = r.spop('tags:article:1')
print(f'弹出: {member}')

# SRANDMEMBER：随机获取（不删除）
r.sadd('lottery', 'A', 'B', 'C', 'D', 'E')
print(r.srandmember('lottery'))  # 随机一个
print(r.srandmember('lottery', 3))  # 随机三个
```

### 集合运算

```python
import redis

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# 准备数据
r.sadd('user:A:hobbies', '读书', '游泳', '编程', '音乐')
r.sadd('user:B:hobbies', '游泳', '跑步', '编程', '绘画')

# 交集（共同爱好）
common = r.sinter('user:A:hobbies', 'user:B:hobbies')
print(f'共同爱好: {common}')  # 输出: {'游泳', '编程'}

# 并集（所有爱好）
all_hobbies = r.sunion('user:A:hobbies', 'user:B:hobbies')
print(f'所有爱好: {all_hobbies}')

# 差集（A 独有）
diff = r.sdiff('user:A:hobbies', 'user:B:hobbies')
print(f'A 独有: {diff}')  # 输出: {'读书', '音乐'}

# 存储结果
r.sinterstore('common_hobbies', 'user:A:hobbies', 'user:B:hobbies')
print(r.smembers('common_hobbies'))  # 输出: {'游泳', '编程'}
```

---

## 六、实战：文章标签系统

```python
import redis

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

class TagSystem:
    """文章标签系统"""

    def __init__(self):
        self.r = redis.Redis(host='localhost', port=6379, decode_responses=True)

    def add_tags(self, article_id, *tags):
        """给文章添加标签"""
        key = f'article:{article_id}:tags'
        self.r.sadd(key, *tags)
        print(f'文章 {article_id} 添加标签: {tags}')

    def get_tags(self, article_id):
        """获取文章的标签"""
        key = f'article:{article_id}:tags'
        return self.r.smembers(key)

    def find_related_articles(self, *tags):
        """查找包含指定标签的文章"""
        # 这里简化处理，实际应该用反向索引
        pass

    def get_common_tags(self, article_id1, article_id2):
        """获取两篇文章的共同标签"""
        key1 = f'article:{article_id1}:tags'
        key2 = f'article:{article_id2}:tags'
        return self.r.sinter(key1, key2)

# 使用示例
ts = TagSystem()

# 添加文章标签
ts.add_tags(1, 'Python', 'Web', 'Django')
ts.add_tags(2, 'Python', 'AI', '机器学习')
ts.add_tags(3, 'Java', 'Web', 'Spring')
ts.add_tags(4, 'Python', 'Web', 'Flask')

# 查看标签
print(f'文章 1 的标签: {ts.get_tags(1)}')

# 找共同标签
common = ts.get_common_tags(1, 2)
print(f'文章 1 和 2 的共同标签: {common}')
# 输出: {'Python'}

common = ts.get_common_tags(1, 4)
print(f'文章 1 和 4 的共同标签: {common}')
# 输出: {'Python', 'Web'}
```

---

## 七、实战：共同好友

```python
import redis

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

class FriendSystem:
    """好友系统"""

    def __init__(self):
        self.r = redis.Redis(host='localhost', port=6379, decode_responses=True)

    def add_friend(self, user_id, friend_id):
        """添加好友"""
        key = f'user:{user_id}:friends'
        self.r.sadd(key, friend_id)
        # 双向好友关系
        self.r.sadd(f'user:{friend_id}:friends', user_id)

    def get_friends(self, user_id):
        """获取好友列表"""
        key = f'user:{user_id}:friends'
        return self.r.smembers(key)

    def get_mutual_friends(self, user_id1, user_id2):
        """获取共同好友"""
        key1 = f'user:{user_id1}:friends'
        key2 = f'user:{user_id2}:friends'
        return self.r.sinter(key1, key2)

    def suggest_friends(self, user_id):
        """推荐好友（好友的好友）"""
        my_friends = self.r.smembers(f'user:{user_id}:friends')
        suggested = set()
        for friend in my_friends:
            friends_of_friend = self.r.smembers(f'user:{friend}:friends')
            suggested.update(friends_of_friend)
        # 去掉自己和已经是好友的人
        suggested.discard(user_id)
        suggested -= my_friends
        return suggested

# 使用示例
fs = FriendSystem()

# 添加好友关系
fs.add_friend('Alice', 'Bob')
fs.add_friend('Alice', 'Charlie')
fs.add_friend('Bob', 'Charlie')
fs.add_friend('Bob', 'David')
fs.add_friend('Charlie', 'Eve')

# 查看好友
print(f'Alice 的好友: {fs.get_friends("Alice")}')
# 输出: {'Bob', 'Charlie'}

# 共同好友
mutual = fs.get_mutual_friends('Alice', 'Bob')
print(f'Alice 和 Bob 的共同好友: {mutual}')
# 输出: {'Charlie'}

# 推荐好友
suggested = fs.suggest_friends('Alice')
print(f'给 Alice 推荐好友: {suggested}')
# 输出: {'David', 'Eve'}
```

---

## 八、本章小结

### 你需要记住的命令

| 命令 | 作用 | 示例 |
|------|------|------|
| `SADD` | 添加成员 | `SADD key member` |
| `SMEMBERS` | 获取所有成员 | `SMEMBERS key` |
| `SISMEMBER` | 判断是否存在 | `SISMEMBER key member` |
| `SCARD` | 成员数量 | `SCARD key` |
| `SREM` | 移除成员 | `SREM key member` |
| `SPOP` | 随机弹出 | `SPOP key` |
| `SRANDMEMBER` | 随机获取 | `SRANDMEMBER key` |
| `SINTER` | 交集 | `SINTER key1 key2` |
| `SUNION` | 并集 | `SUNION key1 key2` |
| `SDIFF` | 差集 | `SDIFF key1 key2` |

### 核心理解

1. Set 是**无序不重复**的集合
2. **集合运算**（交集、并集、差集）是 Set 最强大的功能
3. 适合场景：标签、好友关系、去重统计

### 下章预告

下一章我们会学习**有序集合（Sorted Set）**，实现排行榜功能。

---

> 💡 **动手练习**：
> 1. 用 Set 实现一个去重器（输入一堆数据，输出不重复的）
> 2. 用 SINTER 找两个用户的共同兴趣
> 3. 用 SPOP 实现一个简单的抽奖功能
