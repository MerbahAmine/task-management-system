from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.TaskListCreateView.as_view(), name='task-list-create'),
    path('<int:pk>/', views.TaskDetailView.as_view(), name='task-detail'),
    path('<int:task_id>/comments/', views.TaskCommentListCreateView.as_view(), name='task-comments'),
    path('stats/', views.task_stats, name='task-stats'),
     path('', views.TaskListPageView.as_view(), name='task-list-page'),
]
