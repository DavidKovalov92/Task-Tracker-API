from celery import shared_task
from sendgrid import SendGridAPIClient
from django.utils import timezone
from datetime import timedelta
from sendgrid.helpers.mail import Mail
from .models import Task
from .email import generate_task_email
from .cache import cache_delete_pattern
from project.settings import SENDGRID_API_KEY, DEFAULT_FROM_EMAIL
from django.conf import settings
from django.db.models import Q
import csv
import json
import os
import boto3
from celery import shared_task
from django.conf import settings
from .models import Task


REMINDERS_OFFSETS = [
    timedelta(days=1),
    timedelta(hours=12),
    timedelta(hours=6),
    timedelta(hours=3),
    timedelta(hours=1),
]

@shared_task
def invalidate_task_cache(task_id=None, user_id=None):
    if task_id:
        cache_delete_pattern(f"tasks:detail:{task_id}")
    if user_id:
        cache_delete_pattern(f"tasks:list:{user_id}:*")
    else:
        cache_delete_pattern("tasks:list:*")

@shared_task
def send_email_task(to_email, html_content):
    subject = "You have new tasks"
    
    message = Mail(
        from_email=DEFAULT_FROM_EMAIL,
        to_emails=to_email,
        subject=subject,
        html_content=html_content
    )
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e)


@shared_task
def send_deadline_reminders():
    now = timezone.now()
    for task in Task.objects.filter(assignee_isnull=False, deadline__gt=now):
        for delta in REMINDERS_OFFSETS:
            reminder_time = task.deadline - delta

            if now >= reminder_time and not task.reminder_sent(delta):
                send_email_task.delay(
                    task.assignee.email,
                    generate_task_email(task, task.assignee)
                )
                task.mark_reminder_sent(delta)



@shared_task(ignore_result=False)
def export_tasks_s3(user_id, export_format='csv', filters=None):
    qs = Task.objects.filter(
        Q(assignee_id=user_id) |
        Q(creator_id=user_id) |
        Q(team__members=user_id)
    )

    if filters:
        qs = qs.filter(**filters)

    filename = f'tasks_export_{user_id}.{export_format}'
    local_path = f'/tmp/{filename}'

    if export_format == 'csv':
        with open(local_path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', 'Title', 'Description', 'Deadline', 'Status'])
            for task in qs:
                writer.writerow([
                    task.id,
                    task.title,
                    task.description,
                    task.deadline.isoformat() if task.deadline else '',
                    task.status
                ])
    else:
        data = [
            {
                'id': t.id,
                'title': t.title,
                'description': t.description,
                'deadline': t.deadline.isoformat() if t.deadline else None,
                'status': t.status
            } for t in qs
        ]
        with open(local_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    s3 = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        endpoint_url=settings.AWS_S3_ENDPOINT_URL,
        region_name=settings.AWS_S3_REGION_NAME
    )
    s3.upload_file(local_path, settings.AWS_STORAGE_BUCKET_NAME, f'exports/{filename}')

    url = s3.generate_presigned_url(
        'get_object',
        Params={
            'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
            'Key': f'exports/{filename}'
        },
        ExpiresIn=3600
    )

    os.remove(local_path)

    return url
