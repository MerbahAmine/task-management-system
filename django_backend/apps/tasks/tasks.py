from celery import shared_task
from django.utils.timezone import now
from .models import Task
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_task_notification(task_id, notification_type):
    try:
        task = Task.objects.get(pk=task_id)
        logger.info(f"[{now()}] Notification '{notification_type}' for task '{task.title}' (ID: {task.id})")
        # Here you could integrate with email or Slack, etc.
    except Task.DoesNotExist:
        logger.warning(f"Task with ID {task_id} does not exist")

@shared_task
def generate_daily_summary():
    from django.contrib.auth import get_user_model
    User = get_user_model()
    now_time = now()

    for user in User.objects.all():
        overdue_tasks = user.assigned_tasks.filter(due_date__lt=now_time, status__in=["todo", "in_progress"])
        completed_tasks = user.assigned_tasks.filter(status="done")
        logger.info(f"[Daily Summary] {user.username} → Overdue: {overdue_tasks.count()}, Completed: {completed_tasks.count()}")

@shared_task
def check_overdue_tasks():
    now_time = now()
    from .models import Task
    tasks = Task.objects.filter(due_date__lt=now_time, status__in=['todo', 'in_progress'], is_archived=False)
    
    for task in tasks:
        task.status = 'overdue'  # Add this to STATUS_CHOICES if not there
        task.save()
        logger.info(f"[Overdue Check] Marked Task '{task.title}' as overdue.")
        send_task_notification.delay(task.id, 'overdue')


@shared_task
def cleanup_archived_tasks():
    cutoff = now() - timedelta(days=30)
    from .models import Task
    to_delete = Task.objects.filter(is_archived=True, updated_at__lt=cutoff)
    count = to_delete.count()
    to_delete.delete()
    logger.info(f"[Cleanup] Deleted {count} archived tasks older than 30 days.")
