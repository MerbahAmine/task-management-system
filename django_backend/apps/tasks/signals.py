# apps/tasks/signals.py
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.postgres.search import SearchVector
from .models import Task

@receiver(pre_save, sender=Task)
def update_search_vector(sender, instance, **kwargs):
    instance.search_vector = SearchVector('description', config='english')
