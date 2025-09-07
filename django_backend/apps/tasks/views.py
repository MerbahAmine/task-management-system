from rest_framework import generics, filters, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.utils import timezone
from .models import Task, TaskComment
from .serializers import TaskSerializer, TaskListSerializer, TaskCommentSerializer
from .tasks import send_task_notification


class TaskListCreateView(generics.ListCreateAPIView):
    """View for listing and creating tasks."""
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'assigned_to']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'due_date', 'priority']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(
            Q(created_by=user) | Q(assigned_to=user)
        ).distinct()
    
    def perform_create(self, serializer):
        task = serializer.save()
        # Send notification for new task
        send_task_notification.delay(task.id, 'created')


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """View for retrieving, updating, and deleting individual tasks."""
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(
            Q(created_by=user) | Q(assigned_to=user)
        ).distinct()
    
    def perform_update(self, serializer):
        old_task = self.get_object()
        task = serializer.save()
        
        # Send notification for task updates
        if old_task.status != task.status:
            send_task_notification.delay(task.id, 'status_changed')
        elif old_task.assigned_to != task.assigned_to:
            send_task_notification.delay(task.id, 'assigned')


class TaskCommentListCreateView(generics.ListCreateAPIView):
    """View for listing and creating task comments."""
    serializer_class = TaskCommentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        task_id = self.kwargs['task_id']
        return TaskComment.objects.filter(task_id=task_id)
    
    def perform_create(self, serializer):
        task_id = self.kwargs['task_id']
        task = Task.objects.get(id=task_id)
        serializer.save(author=self.request.user, task=task)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def task_stats(request):
    """View for getting task statistics for the current user."""
    user = request.user
    tasks = Task.objects.filter(
        Q(created_by=user) | Q(assigned_to=user)
    ).distinct()
    
    stats = {
        'total_tasks': tasks.count(),
        'todo_tasks': tasks.filter(status='todo').count(),
        'in_progress_tasks': tasks.filter(status='in_progress').count(),
        'review_tasks': tasks.filter(status='review').count(),
        'done_tasks': tasks.filter(status='done').count(),
        'overdue_tasks': tasks.filter(due_date__lt=timezone.now(), status__in=['todo', 'in_progress', 'review']).count(),
    }
    
    return Response(stats)
