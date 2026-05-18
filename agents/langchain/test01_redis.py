import redis

r = redis.Redis(host='localhost', port=6379, decode_responses=True, password='123456')
r.set('name', '李明')
print(r.get('name'))
# print(r.keys('*'))
print(r.type('name'))
print(r.exists('name'))