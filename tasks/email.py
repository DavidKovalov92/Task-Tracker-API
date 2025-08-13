def generate_task_email(task, assigned_by):
    deadline_text = task.deadline.strftime("%d.%m.%Y %H:%M") if task.deadline else "не указан"

    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <h2>Вам назначена новая задача</h2>
            <p><strong>Название:</strong> {task.title}</p>
            <p><strong>Дедлайн:</strong> {deadline_text}</p>
            <p><strong>Назначил:</strong> {assigned_by.get_full_name() or assigned_by.username}</p>
            <p><strong>ID задачи:</strong> {task.id}</p>
        </body>
    </html>
    """
    return html_content

