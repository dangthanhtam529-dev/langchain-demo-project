# 第 6 章：哈希（Hash）——存储对象

> 本章目标：学会用 Hash 存储结构化的对象数据。

---

## 一、为什么要用 Hash？

### 先看看不用 Hash 的方式

假设你要存一个用户的信息：

```
SET user:1:name "张三"
SET user:1:age "25"
SET user:1:email "zhangsan@example.com"
SET user:1:city "北京"
```

**问题：**
1. 用了 4 个独立的键，浪费内存
2. 获取用户全部信息需要 4 次操作
3. 删除用户需要删除 4 个键
4. 键名很长，管理麻烦

### 用 Hash 的方式

```
HSET user:1 name "张三" age 25 email "zhangsan@example.com" city "北京"
```

**好处：**
1. 所有信息存在一个键里
2. 一次操作就能获取全部信息
3. 删除时只需删除一个键
4. 可以单独操作某个字段

---

## 二、Hash 是什么？

Hash 就是一个**键值对的集合**，类似于 Python 的字典。

```
┌──────────────────────────────────────────┐
│  键: user:1                              │
│  ┌────────────────────────────────────┐  │
│  │  字段(field)  →  值(value)         │  │
│  ├────────────────────────────────────┤  │
│  │  name        →  "张三"             │  │
│  │  age         →  "25"               │  │
│  │  email       →  "zhangsan@..."     │  │
│  │  city        →  "北京"             │  │
│  └────────────────────────────────────┘  │
└──────────────────────────────────────────┘
```

**术语说明：**
- **键（key）**：整个 Hash 的名字，如 `user:1`
- **字段（field）**：Hash 内部的属性名，如 `name`、`age`
- **值（value）**：字段对应的值

---

## 三、基本操作

### HSET：设置字段

```
127.0.0.1:6379> HSET user:1 name "张三"
(integer) 1

127.0.0.1:6379> HSET user:1 age 25
(integer) 1

127.0.0.1:6379> HSET user:1 email "zhangsan@example.com"
(integer) 1
```

**或者一次性设置多个字段：**

```
127.0.0.1:6379> HSET user:1 name "张三" age 25 email "zhangsan@example.com" city "北京"
(integer) 4
```

返回的 `4` 表示新增了 4 个字段。

### HGET：获取单个字段

```
127.0.0.1:6379> HGET user:1 name
"张三"

127.0.0.1:6379> HGET user:1 age
"25"
```

### HGETALL：获取所有字段和值

```
127.0.0.1:6379> HGETALL user:1
1) "name"
2) "张三"
3) "age"
4) "25"
5) "email"
6) "zhangsan@example.com"
7) "city"
8) "北京"
```

**注意：** 返回结果是交替的：字段名、值、字段名、值...
在 Python 中会自动转成字典。

---

## 四、字段操作

### HMGET：获取多个字段

```
127.0.0.1:6379> HMGET user:1 name email
1) "张三"
2) "zhangsan@example.com"
```

### HDEL：删除字段

```
127.0.0.1:6379> HDEL user:1 city
(integer) 1

127.0.0.1:6379> HGETALL user:1
1) "name"
2) "张三"
3) "age"
4) "25"
5) "email"
6) "zhangsan@example.com"
```

city 字段被删除了。

### HEXISTS：判断字段是否存在

```
127.0.0.1:6379> HEXISTS user:1 name
(integer) 1

127.0.0.1:6379> HEXISTS user:1 city
(integer) 0
```

返回 `1` 表示存在，`0` 表示不存在。

---

## 五、查看 Hash 信息

### HLEN：获取字段数量

```
127.0.0.1:6379> HLEN user:1
(integer) 3
```

### HKEYS：获取所有字段名

```
127.0.0.1:6379> HKEYS user:1
1) "name"
2) "age"
3) "email"
```

### HVALS：获取所有字段值

```
127.0.0.1:6379> HVALS user:1
1) "张三"
2) "25"
3) "zhangsan@example.com"
```

---

## 六、字段数字操作

Hash 中的字段如果是数字，也可以进行运算：

```
127.0.0.1:6379> HSET user:1 score 100
(integer) 1

127.0.0.1:6379> HINCRBY user:1 score 10
(integer) 110

127.0.0.1:6379> HINCRBY user:1 score -20
(integer) 90

127.0.0.1:6379> HGET user:1 score
"90"
```

**解释：**
- `HINCRBY`：Hash Increment By，Hash 字段自增
- 和 `INCRBY` 类似，只是操作的是 Hash 内部的字段

---

## 七、Python 代码

```python
import redis

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# HSET：设置字段
r.hset('user:1', 'name', '张三')
r.hset('user:1', 'age', 25)
r.hset('user:1', 'email', 'zhangsan@example.com')

# 或者用 mapping 一次性设置多个字段
r.hset('user:1', mapping={
    'name': '张三',
    'age': 25,
    'email': 'zhangsan@example.com',
    'city': '北京'
})

# HGET：获取单个字段
print(r.hget('user:1', 'name'))  # 输出: 张三

# HGETALL：获取所有字段（返回字典）
print(r.hgetall('user:1'))
# 输出: {'name': '张三', 'age': '25', 'email': 'zhangsan@example.com', 'city': '北京'}

# HMGET：获取多个字段
print(r.hmget('user:1', ['name', 'email']))
# 输出: ['张三', 'zhangsan@example.com']

# HDEL：删除字段
r.hdel('user:1', 'city')
print(r.hgetall('user:1'))
# 输出: {'name': '张三', 'age': '25', 'email': 'zhangsan@example.com'}

# HEXISTS：判断字段是否存在
print(r.hexists('user:1', 'name'))  # 输出: True
print(r.hexists('user:1', 'city'))  # 输出: False

# HLEN：字段数量
print(r.hlen('user:1'))  # 输出: 3

# HKEYS：所有字段名
print(r.hkeys('user:1'))  # 输出: ['name', 'age', 'email']

# HVALS：所有字段值
print(r.hvals('user:1'))  # 输出: ['张三', '25', 'zhangsan@example.com']

# HINCRBY：字段自增
r.hset('user:1', 'score', 100)
r.hincrby('user:1', 'score', 50)
print(r.hget('user:1', 'score'))  # 输出: 150
```

---

## 八、实战：商品管理系统

```python
import redis

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

class ProductManager:
    """商品管理"""

    def __init__(self):
        self.r = redis.Redis(host='localhost', port=6379, decode_responses=True)

    def add_product(self, product_id, name, price, stock, category):
        """添加商品"""
        key = f'product:{product_id}'
        self.r.hset(key, mapping={
            'name': name,
            'price': str(price),
            'stock': str(stock),
            'category': category,
            'sales': '0'  # 初始销量为 0
        })
        print(f'商品 {name} 已添加')

    def get_product(self, product_id):
        """获取商品信息"""
        key = f'product:{product_id}'
        product = self.r.hgetall(key)
        if not product:
            print('商品不存在')
            return None
        return product

    def update_stock(self, product_id, change):
        """更新库存（正数增加，负数减少）"""
        key = f'product:{product_id}'
        new_stock = self.r.hincrby(key, 'stock', change)
        if new_stock < 0:
            print('库存不足')
            return False
        print(f'库存已更新，当前: {new_stock}')
        return True

    def increase_sales(self, product_id):
        """销量 +1"""
        key = f'product:{product_id}'
        self.r.hincrby(key, 'sales', 1)

    def get_product_field(self, product_id, field):
        """获取商品某个字段"""
        key = f'product:{product_id}'
        return self.r.hget(key, field)

# 使用示例
pm = ProductManager()

# 添加商品
pm.add_product('P001', 'iPhone 15', 5999, 100, '手机')
pm.add_product('P002', 'MacBook Pro', 14999, 50, '电脑')
pm.add_product('P003', 'AirPods Pro', 1999, 200, '耳机')

# 查看商品
product = pm.get_product('P001')
print(product)
# 输出: {'name': 'iPhone 15', 'price': '5999', 'stock': '100', 'category': '手机', 'sales': '0'}

# 模拟购买（库存 -1，销量 +1）
pm.update_stock('P001', -1)
pm.increase_sales('P001')

# 查看库存
stock = pm.get_product_field('P001', 'stock')
sales = pm.get_product_field('P001', 'sales')
print(f'库存: {stock}, 销量: {sales}')
# 输出: 库存: 99, 销量: 1
```

---

## 九、Hash vs JSON 字符串

你可能想问：为什么不直接把整个字典转成 JSON 存成字符串？

```python
# 方式 1：JSON 字符串
r.set('user:1', json.dumps({'name': '张三', 'age': 25}))

# 方式 2：Hash
r.hset('user:1', mapping={'name': '张三', 'age': 25})
```

| 对比项 | JSON 字符串 | Hash |
|--------|------------|------|
| 获取单个字段 | 需要取出整个 JSON 再解析 | 直接 `HGET` |
| 更新单个字段 | 需要取出、修改、存回 | 直接 `HSET` |
| 内存占用 | 稍大 | 更省（Redis 有优化） |
| 字段运算 | 不支持 | 支持 `HINCRBY` |

**结论：** 存储结构化对象时，**优先使用 Hash**。

---

## 十、本章小结

### 你需要记住的命令

| 命令 | 作用 | 示例 |
|------|------|------|
| `HSET` | 设置字段 | `HSET key field value` |
| `HGET` | 获取字段 | `HGET key field` |
| `HGETALL` | 获取所有字段 | `HGETALL key` |
| `HMGET` | 获取多个字段 | `HMGET key f1 f2` |
| `HDEL` | 删除字段 | `HDEL key field` |
| `HEXISTS` | 字段是否存在 | `HEXISTS key field` |
| `HLEN` | 字段数量 | `HLEN key` |
| `HINCRBY` | 字段自增 | `HINCRBY key field 10` |

### 核心理解

1. Hash 适合存储**结构化的对象数据**
2. 可以单独操作某个字段，不需要取出整个对象
3. Hash 字段也支持数字运算（`HINCRBY`）

### 下章预告

下一章我们会学习**列表（List）**，实现消息队列功能。

---

> 💡 **动手练习**：
> 1. 用 Hash 存储你自己的信息（姓名、年龄、爱好等）
> 2. 用 HINCRBY 实现一个积分系统
> 3. 用 Python 写一个完整的商品管理小系统
