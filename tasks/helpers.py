from .models import TaskChangeLog, NotificationLog, NotificationType, NotificationStatus


def task_change_log(task, user, field_changed, old_value, new_value):
    return TaskChangeLog.objects.create(
        task=task,
        user=user,
        field_changed=field_changed,
        old_value=old_value,
        new_value=new_value
    )

def log_notification(task, user, notif_type=NotificationType.ASSIGN, status=NotificationStatus.SENT):
    return NotificationLog.objects.create(
        task=task,
        user=user,
        type=notif_type,
        status=status
    )