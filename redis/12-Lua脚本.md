# 第 12 章：Lua 脚本

> 本章目标：学会用 Lua 脚本实现复杂的原子操作。

---

## 一、为什么需要 Lua 脚本？

### 先看一个问题

假设你要实现一个"如果键不存在就设置，存在就返回当前值"的操作：

```python
# 方式 1：用 Python 代码
value = r.get('mykey')
if value is None:
    r.set('mykey', 'newvalue')
    return '已设置'
else:
    return value
```

**问题：** 这不是原子操作。如果两个客户端同时执行：

```
客户端 A: GET → None
客户端 B: GET → None
客户端 A: SET → 'newvalue'
客户端 B: SET → 'newvalue'  ← 重复设置了
```

### Lua 脚本的解决方案

```lua
local current = redis.call('GET', KEYS[1])
if current then
    return current
else
    redis.call('SET', KEYS[1], ARGV[1])
    return '已设置'
end
```

**Lua 脚本在 Redis 中是原子执行的**，不会被其他命令打断。

---

## 二、Lua 脚本基础

### EVAL 命令

```
EVAL script numkeys key1 key2 ... arg1 arg2 ...
```

**参数说明：**
- `script`：Lua 脚本代码
- `numkeys`：后面有几个键参数
- `key1 key2 ...`：键参数，在脚本中用 `KEYS[1]`、`KEYS[2]` 访问
- `arg1 arg2 ...`：值参数，在脚本中用 `ARGV[1]`、`ARGV[2]` 访问

### 第一个 Lua 脚本

```
127.0.0.1:6379> EVAL "return 'Hello Redis'" 0
"Hello Redis"
```

这是最简单的脚本，直接返回一个字符串。

### 访问键参数

```
127.0.0.1:6379> SET mykey "原始值"
OK

127.0.0.1:6379> EVAL "return redis.call('GET', KEYS[1])" 1 mykey
"原始值"
```

**解释：**
- `redis.call('GET', KEYS[1])`：在 Lua 中执行 Redis 命令
- `KEYS[1]`：第一个键参数（mykey）
- `1`：表示后面有 1 个键参数

### 访问值参数

```
127.0.0.1:6379> EVAL "redis.call('SET', KEYS[1], ARGV[1]); return 'OK'" 1 mykey "新值"
"OK"

127.0.0.1:6379> GET mykey
"新值"
```

**解释：**
- `ARGV[1]`：第一个值参数（"新值"）

---

## 三、常用 Lua 操作

### 条件判断

```lua
local value = redis.call('GET', KEYS[1])
if value then
    return '键存在，值: ' .. value
else
    return '键不存在'
end
```

**说明：** `..` 是 Lua 的字符串连接符。

### 数字运算

```lua
local current = tonumber(redis.call('GET', KEYS[1]))
if current < 100 then
    redis.call('INCRBY', KEYS[1], 10)
    return '已增加'
else
    return '已达上限'
end
```

**说明：** `tonumber()` 把字符串转成数字。

### 循环

```lua
local count = 0
for i = 1, 10 do
    redis.call('INCR', KEYS[1])
    count = count + 1
end
return count
```

---

## 四、Python 中使用 Lua 脚本

### 方式 1：直接执行

```python
import redis

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Lua 脚本
lua_script = """
local current = redis.call('GET', KEYS[1])
if current then
    return tonumber(current) + tonumber(ARGV[1])
else
    return ARGV[1]
end
"""

# 执行
result = r.eval(lua_script, 1, 'counter', 10)
print(result)  # 输出: 10

result = r.eval(lua_script, 1, 'counter', 5)
print(result)  # 输出: 15
```

### 方式 2：注册脚本（推荐）

```python
import redis

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

lua_script = """
local current = redis.call('GET', KEYS[1])
if current then
    return tonumber(current) + tonumber(ARGV[1])
else
    return ARGV[1]
end
"""

# 注册脚本（会缓存 SHA1）
script = r.register_script(lua_script)

# 执行
result = script(keys=['counter'], args=[10])
print(result)  # 输出: 10

result = script(keys=['counter'], args=[5])
print(result)  # 输出: 15
```

**为什么推荐注册？**
- 第一次执行时，Redis 会缓存脚本的 SHA1 哈希
- 后续执行只需传 SHA1，不用重复发送脚本内容
- 更高效

---

## 五、实战：限流器

这是 Lua 脚本最经典的应用场景。

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
    return 0  -- 超过限制，拒绝
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
    """
    检查用户是否在限流范围内

    参数:
        user_id: 用户 ID
        limit: 时间窗口内允许的最大请求数
        window: 时间窗口（秒）

    返回:
        True 允许，False 拒绝
    """
    key = f'rate_limit:{user_id}'
    result = script(keys=[key], args=[limit, window])
    return result == 1

# 测试
print('限流测试（60 秒内最多 5 次）:\n')
for i in range(7):
    allowed = check_rate_limit('user:1', limit=5, window=60)
    status = '允许' if allowed else '拒绝'
    print(f'请求 {i+1}: {status}')

# 输出:
# 限流测试（60 秒内最多 5 次）:
#
# 请求 1: 允许
# 请求 2: 允许
# 请求 3: 允许
# 请求 4: 允许
# 请求 5: 允许
# 请求 6: 拒绝
# 请求 7: 拒绝
```

**脚本逻辑解析：**

```lua
-- 1. 获取参数
local key = KEYS[1]           -- 限流键
local limit = tonumber(ARGV[1])  -- 最大请求数
local window = tonumber(ARGV[2]) -- 时间窗口

-- 2. 获取当前请求数
local current = tonumber(redis.call('GET', key) or "0")

-- 3. 判断是否超过限制
if current + 1 > limit then
    return 0  -- 拒绝
else
    -- 4. 请求数 +1
    redis.call('INCR', key)
    -- 5. 如果是第一次请求，设置过期时间
    if current == 0 then
        redis.call('EXPIRE', key, window)
    end
    return 1  -- 允许
end
```

---

## 六、实战：分布式锁

```python
import redis
import time

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# 获取锁的 Lua 脚本
acquire_lock_script = """
if redis.call('EXISTS', KEYS[1]) == 0 then
    redis.call('SET', KEYS[1], ARGV[1], 'EX', ARGV[2])
    return 1
else
    return 0
end
"""

# 释放锁的 Lua 脚本
release_lock_script = """
if redis.call('GET', KEYS[1]) == ARGV[1] then
    redis.call('DEL', KEYS[1])
    return 1
else
    return 0
end
"""

acquire_script = r.register_script(acquire_lock_script)
release_script = r.register_script(release_lock_script)

class DistributedLock:
    """分布式锁"""

    def __init__(self, name, timeout=10):
        self.name = f'lock:{name}'
        self.timeout = timeout
        self.identifier = f'{id(self)}:{time.time()}'
        self.r = redis.Redis(host='localhost', port=6379, decode_responses=True)

    def acquire(self):
        """获取锁"""
        result = acquire_script(
            keys=[self.name],
            args=[self.identifier, self.timeout]
        )
        if result == 1:
            print(f'获取锁成功: {self.name}')
            return True
        else:
            print(f'获取锁失败: {self.name}（已被占用）')
            return False

    def release(self):
        """释放锁"""
        result = release_script(
            keys=[self.name],
            args=[self.identifier]
        )
        if result == 1:
            print(f'释放锁成功: {self.name}')
            return True
        else:
            print(f'释放锁失败: {self.name}（锁已过期或被他人持有）')
            return False

# 使用示例
lock = DistributedLock('resource:A', timeout=5)

# 获取锁
if lock.acquire():
    try:
        # 执行需要互斥的操作
        print('正在执行关键操作...')
        time.sleep(2)
    finally:
        # 确保锁被释放
        lock.release()

# 输出:
# 获取锁成功: lock:resource:A
# 正在执行关键操作...
# 释放锁成功: lock:resource:A
```

**为什么用 Lua 脚本实现锁？**

```
不用 Lua：
1. 检查锁是否存在
2. 不存在则设置锁
← 步骤 1 和 2 之间可能被其他客户端插入

用 Lua：
1 和 2 在 Lua 脚本中原子执行
← 不会被其他命令打断
```

---

## 七、实战：原子性库存扣减

```python
import redis

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# 库存扣减脚本
deduct_stock_script = """
local stock = tonumber(redis.call('GET', KEYS[1]))
if stock and stock >= tonumber(ARGV[1]) then
    redis.call('DECRBY', KEYS[1], ARGV[1])
    redis.call('INCRBY', KEYS[2], ARGV[1])
    return 1  -- 扣减成功
else
    return 0  -- 库存不足
end
"""

deduct_script = r.register_script(deduct_stock_script)

def buy_product(product_id, quantity):
    """购买商品"""
    stock_key = f'stock:{product_id}'
    sold_key = f'sold:{product_id}'

    result = deduct_script(
        keys=[stock_key, sold_key],
        args=[quantity]
    )

    if result == 1:
        print(f'购买成功: {quantity} 件')
        return True
    else:
        print('库存不足')
        return False

# 初始化库存
r.set('stock:iPhone15', 10)
r.set('sold:iPhone15', 0)

# 购买测试
buy_product('iPhone15', 3)
buy_product('iPhone15', 5)
buy_product('iPhone15', 3)  # 库存只剩 2，应该失败

print(f'剩余库存: {r.get("stock:iPhone15")}')
print(f'已售出: {r.get("sold:iPhone15")}')

# 输出:
# 购买成功: 3 件
# 购买成功: 5 件
# 库存不足
# 剩余库存: 2
# 已售出: 8
```

---

## 八、本章小结

### 你需要记住的命令

| 命令 | 作用 | 示例 |
|------|------|------|
| `EVAL` | 执行 Lua 脚本 | `EVAL script numkeys key arg` |
| `EVALSHA` | 用 SHA1 执行 | `EVALSHA sha1 numkeys key arg` |
| `SCRIPT LOAD` | 加载脚本 | `SCRIPT LOAD script` |
| `SCRIPT EXISTS` | 检查脚本是否存在 | `SCRIPT EXISTS sha1` |

### 核心理解

1. Lua 脚本在 Redis 中是**原子执行**的
2. `KEYS[]` 访问键参数，`ARGV[]` 访问值参数
3. `register_script()` 会缓存脚本，更高效
4. 适合场景：限流器、分布式锁、复杂原子操作

### 下章预告

下一章我们会学习**Redis JSON**，在 Redis 中原生操作 JSON 数据。

---

> 💡 **动手练习**：
> 1. 写一个 Lua 脚本实现"如果键存在就删除，不存在就创建"
> 2. 用 Lua 脚本实现一个简单的计数器（带最大值限制）
> 3. 用 Lua 脚本实现批量删除指定前缀的键
