from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import Task


@shared_task
def send_task_notification(task_id, notification_type):
    """Send notification for task events."""
    try:
        task = Task.objects.get(id=task_id)
        
        if notification_type == 'created':
            subject = f'New Task Created: {task.title}'
            message = f'A new task "{task.title}" has been created and assigned to you.'
        elif notification_type == 'status_changed':
            subject = f'Task Status Updated: {task.title}'
            message = f'Task "{task.title}" status has been changed to {task.get_status_display()}.'
        elif notification_type == 'assigned':
            subject = f'Task Assigned: {task.title}'
            message = f'Task "{task.title}" has been assigned to you.'
        else:
            return
        
        # Send email notification if assigned user has email
        if task.assigned_to and task.assigned_to.email:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[task.assigned_to.email],
                fail_silently=True,
            )
        
        return f'Notification sent for task {task_id}'
    except Task.DoesNotExist:
        return f'Task {task_id} not found'
    except Exception as e:
        return f'Error sending notification: {str(e)}'


@shared_task
def cleanup_old_tasks():
    """Cleanup old completed tasks (older than 30 days)."""
    from django.utils import timezone
    from datetime import timedelta
    
    cutoff_date = timezone.now() - timedelta(days=30)
    old_tasks = Task.objects.filter(
        status='done',
        completed_at__lt=cutoff_date
    )
    
    count = old_tasks.count()
    old_tasks.delete()
    
    return f'Cleaned up {count} old completed tasks'


@shared_task
def send_overdue_task_reminders():
    """Send reminders for overdue tasks."""
    from django.utils import timezone
    
    overdue_tasks = Task.objects.filter(
        due_date__lt=timezone.now(),
        status__in=['todo', 'in_progress', 'review']
    )
    
    for task in overdue_tasks:
        if task.assigned_to and task.assigned_to.email:
            send_mail(
                subject=f'Overdue Task Reminder: {task.title}',
                message=f'Task "{task.title}" is overdue. Please update its status.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[task.assigned_to.email],
                fail_silently=True,
            )
    
    return f'Sent reminders for {overdue_tasks.count()} overdue tasks'
