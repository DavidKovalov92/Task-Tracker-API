from celery import shared_task
from sendgrid import SendGridAPIClient
from django.utils import timezone
from datetime import timedelta
from sendgrid.helpers.mail import Mail
from .models import Task
from .email import generate_task_email
from .cache import cache_delete_pattern
from project.settings import SENDGRID_API_KEY, DEFAULT_FROM_EMAIL


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









