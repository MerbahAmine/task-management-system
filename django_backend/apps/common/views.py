from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.http import JsonResponse


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint for monitoring."""
    return Response({
        'status': 'healthy',
        'message': 'Task Management System is running',
        'version': '1.0.0'
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def api_info(request):
    """API information endpoint."""
    return Response({
        'name': 'Task Management System API',
        'version': '1.0.0',
        'description': 'A comprehensive task management system built with Django and Docker',
        'endpoints': {
            'auth': '/api/v1/auth/',
            'tasks': '/api/v1/tasks/',
            'health': '/api/v1/health/',
            'admin': '/admin/',
        }
    })
