from django.urls import path
from . import views

urlpatterns = [
    # API endpoints
    path('', views.TaskListCreateView.as_view(), name='task-list-create'),
    path('<int:pk>/', views.TaskDetailView.as_view(), name='task-detail'),
    path('<int:task_id>/comments/', views.TaskCommentListCreateView.as_view(), name='task-comments'),
    path('stats/', views.task_stats, name='task-stats'),

    # Frontend pages
    path('page/', views.TaskListPageView.as_view(), name='task-list-page'),
    path('page/<int:pk>/', views.TaskDetailPageView.as_view(), name='task-detail-page'),
    path('page/create/', views.TaskCreatePageView.as_view(), name='task-create-page'),
]
