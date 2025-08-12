from celery import shared_task
from .cache import cache_delete_pattern

@shared_task
def invalidate_task_cache(task_id=None, user_id=None):
    if task_id:
        cache_delete_pattern(f"tasks:detail:{task_id}")
    if user_id:
        cache_delete_pattern(f"tasks:list:{user_id}:*")
    else:
        cache_delete_pattern("tasks:list:*")
