from rest_framework import generics, filters, status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.utils import timezone
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView, DetailView, CreateView
from .models import Task, Comment, TaskHistory
from .serializers import TaskSerializer, CommentSerializer, TaskHistorySerializer
from .tasks import send_task_notification
from rest_framework.filters import SearchFilter, OrderingFilter




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
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        task_id = self.kwargs['task_id']
        return Comment.objects.filter(task_id=task_id)
    
    def perform_create(self, serializer):
        task_id = self.kwargs['task_id']
        task = Task.objects.get(id=task_id)
        serializer.save(user=self.request.user, task=task)


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




class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.filter(is_archived=False)
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'priority', 'created_by']
    search_fields = ['title', 'description']
    ordering_fields = ['due_date', 'priority', 'created_at']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_destroy(self, instance):
        instance.soft_delete()

    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        task = self.get_object()
        user_ids = request.data.get('user_ids', [])
        if not isinstance(user_ids, list):
            return Response({'error': 'user_ids must be a list'}, status=status.HTTP_400_BAD_REQUEST)
        users = get_user_model().objects.filter(id__in=user_ids)
        task.assigned_to.add(*users)
        return Response({'status': 'users assigned'})

    @action(detail=True, methods=['post'])
    def comments(self, request, pk=None):
        task = self.get_object()
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, task=task)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def list_comments(self, request, pk=None):
        task = self.get_object()
        comments = task.comments.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        task = self.get_object()
        history = task.history.all()
        serializer = TaskHistorySerializer(history, many=True)
        return Response(serializer.data)
class TaskListPageView(LoginRequiredMixin, ListView):
    template_name = 'tasks/task_list.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(Q(created_by=user) | Q(assigned_to=user)).distinct().order_by('-created_at')


class TaskDetailPageView(LoginRequiredMixin, DetailView):
    template_name = 'tasks/task_detail.html'
    model = Task
    context_object_name = 'task'


class TaskCreatePageView(LoginRequiredMixin, CreateView):
    template_name = 'tasks/task_form.html'
    model = Task
    fields = ['title', 'description', 'status', 'priority', 'due_date', 'estimated_hours']

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        return response

    def get_success_url(self):
        return reverse_lazy('task-detail-page', kwargs={'pk': self.object.pk})