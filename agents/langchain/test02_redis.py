import redis

r = redis.Redis(host='localhost', port=6379, decode_responses=True, password='123456')
# 文章id
# article_id = '100001'
# r.set("view", 0)
# print(r.get("view"))
# print(f'文章{article_id}的当前访问量: {r.incr("view")}')

from datetime import datetime


class VisitCounter:
    """网站访问统计"""

    def __init__(self):
        self.r = redis.Redis(host='localhost', port=6379, decode_responses=True)

    def record_visit(self, page):
        """记录一次页面访问"""
        today = datetime.now().strftime('%Y-%m-%d')
        key = f'visits:{today}:{page}'
        self.r.incr(key)
        print(f'页面 {page} 访问次数 +1')

    def get_visits(self, page, date=None):
        """获取页面访问次数"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        key = f'visits:{date}:{page}'
        count = self.r.get(key)
        return int(count) if count else 0

    def get_total_visits(self, date=None):
        """获取当天总访问量"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        # 获取当天所有页面的访问键
        keys = self.r.keys(f'visits:{date}:*')
        total = 0
        for key in keys:
            count = self.r.get(key)
            if count:
                total += int(count)
        return total

# 使用示例
counter = VisitCounter()

# 记录访问
counter.record_visit('首页')
counter.record_visit('首页')
counter.record_visit('关于我们')
counter.record_visit('首页')

# 查看统计
print(f'首页今天被访问了 {counter.get_visits("首页")} 次')
# 输出: 首页今天被访问了 3 次

print(f'关于我们今天被访问了 {counter.get_visits("关于我们")} 次')