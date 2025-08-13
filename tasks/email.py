def generate_task_email(task, assigned_by):
    deadline_text = task.deadline.strftime("%d.%m.%Y %H:%M") if task.deadline else "не указан"

    html_content = f"""
    <html>
      <body style="font-family: Arial, sans-serif; background-color: #f7f7f7; margin: 0; padding: 0;">
        <table align="center" width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); padding: 20px;">
          <tr>
            <td style="text-align: center; padding-bottom: 20px;">
              <h1 style="color: #2F80ED;">Новая задача назначена</h1>
            </td>
          </tr>
          <tr>
            <td style="padding: 10px 0;">
              <p><strong>Название:</strong> {task.title}</p>
              <p><strong>Дедлайн:</strong> {deadline_text}</p>
              <p><strong>Назначил:</strong> {assigned_by.get_full_name() or assigned_by.username}</p>
              <p><strong>ID задачи:</strong> {task.id}</p>
            </td>
          </tr>
          <tr>
            <td style="text-align: center; padding: 20px 0;">
              <a href="https://yourapp.example.com/tasks/{task.id}" style="background-color: #2F80ED; color: #ffffff; padding: 12px 25px; text-decoration: none; border-radius: 5px; display: inline-block;">Перейти к задаче</a>
            </td>
          </tr>
          <tr>
            <td style="font-size: 12px; color: #888888; padding-top: 20px; text-align: center;">
              Вы получили это письмо, потому что являетесь участником проекта.<br>
              Если вы не хотите получать уведомления, измените настройки уведомлений в вашем аккаунте.
            </td>
          </tr>
        </table>
      </body>
    </html>
    """
    return html_content


