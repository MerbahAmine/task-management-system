
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.users.views import UserViewSet
from apps.tasks.views import TaskViewSet


router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'tasks', TaskViewSet, basename='tasks')
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/auth/', include('apps.users.urls')),
    path('api/tasks/', include('apps.tasks.urls')),
    path('tasks/', include('apps.tasks.urls')),
    path('', include('apps.tasks.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
]
   
    
    
