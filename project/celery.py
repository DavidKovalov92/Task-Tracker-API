import os
from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

app = Celery('project', broker='redis://redis:6379/0', backend='redis://redis:6379/1')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()