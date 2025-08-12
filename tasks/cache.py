import json
import hashlib
from django_redis import get_redis_connection

redis_client = get_redis_connection("default")

def make_cache_key(user_id, base_key, query_params):
    query_string = json.dumps(query_params, sort_keys=True)
    query_hash = hashlib.md5(query_string.encode()).hexdigest()
    return f"{base_key}:{user_id}:{query_hash}"

def cache_set(key, data, ttl=120):
    redis_client.set(key, json.dumps(data), ex=ttl)

def cache_get(key):
    data = redis_client.get(key)
    if data:
        return json.loads(data)
    return None

def cache_delete_pattern(pattern):
    keys = redis_client.keys(pattern)
    if keys:
        redis_client.delete(*keys)

