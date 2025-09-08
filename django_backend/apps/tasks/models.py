# apps/tasks/models.py
from django.conf import settings
from django.db import models
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField

STATUS_CHOICES = (
    ('todo', 'To Do'),
    ('in_progress', 'In Progress'),
    ('done', 'Done'),
)

PRIORITY_CHOICES = (
    ('low', 'Low'),
    ('medium', 'Medium'),
    ('high', 'High'),
)

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES)
    due_date = models.DateTimeField()
    estimated_hours = models.DecimalField(max_digits=6, decimal_places=2)
    actual_hours = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_tasks')
    assigned_to = models.ManyToManyField(settings.AUTH_USER_MODEL, through='TaskAssignment', related_name='assigned_tasks')
    tags = models.ManyToManyField(Tag, blank=True)
    parent_task = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)

    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_archived = models.BooleanField(default=False)

    search_vector = SearchVectorField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
            models.Index(fields=['due_date']),
            GinIndex(fields=['search_vector']),
        ]

    def soft_delete(self):
        self.is_archived = True
        self.save()

class TaskAssignment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('task', 'user')

class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class TaskHistory(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='history')
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    change_description = models.TextField()

class Team(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='teams')

class TaskTemplate(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    default_status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    default_priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES)
    estimated_hours = models.DecimalField(max_digits=6, decimal_places=2)
