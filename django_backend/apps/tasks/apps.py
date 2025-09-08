from django.apps import AppConfig
from django_celery_beat.models import PeriodicTask, IntervalSchedule, CrontabSchedule
import json

class TasksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.tasks'

    def ready(self):
        from . import signals  # if using signals
        from django_celery_beat.models import PeriodicTask, CrontabSchedule
        from django.db.utils import OperationalError

        try:
            # Daily summary at 8AM UTC
            schedule, _ = CrontabSchedule.objects.get_or_create(hour=8, minute=0)
            PeriodicTask.objects.get_or_create(
                crontab=schedule,
                name='Daily Summary',
                task='apps.tasks.tasks.generate_daily_summary',
            )

            # Check overdue tasks every hour
            hourly, _ = CrontabSchedule.objects.get_or_create(minute=0)
            PeriodicTask.objects.get_or_create(
                crontab=hourly,
                name='Check Overdue Tasks',
                task='apps.tasks.tasks.check_overdue_tasks',
            )

            # Cleanup weekly (Sunday 00:00)
            weekly, _ = CrontabSchedule.objects.get_or_create(minute=0, hour=0, day_of_week='0')
            PeriodicTask.objects.get_or_create(
                crontab=weekly,
                name='Cleanup Archived Tasks',
                task='apps.tasks.tasks.cleanup_archived_tasks',
            )

        except OperationalError:
            # For migrations and initial setup
            pass
