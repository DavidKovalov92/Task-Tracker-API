from celery import shared_task
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from .cache import cache_delete_pattern
from project.settings import SENDGRID_API_KEY, DEFAULT_FROM_EMAIL

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
def send_deadline_reminder(assignee_email, task_title, deadline):
    subject = f"Reminder: Task '{task_title}' is approaching!"
    html_content = f"""
        <p>Hi!</p>
        <p>This is a reminder that your task <b>{task_title}</b> is due on <b>{deadline}</b>.</p>
        <p>Don't forget to complete it on time!</p>
    """

    message = Mail(
        from_email=DEFAULT_FROM_EMAIL,
        to_emails=assignee_email,
        subject=subject,
        html_content=html_content
    )

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        sg.send(message)
    except Exception as e:
        print(f"Email error: {e}")




