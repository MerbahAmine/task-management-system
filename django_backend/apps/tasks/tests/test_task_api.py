from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class TaskAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user1', password='pass123')
        self.client.login(username='user1', password='pass123')

    def test_create_task(self):
        url = reverse('tasks-list')
        data = {
            "title": "Test Task",
            "description": "Task desc",
            "status": "todo",
            "priority": "medium",
            "due_date": "2030-01-01T00:00:00Z",
            "estimated_hours": "5",
            "assigned_to": [],
            "tags": [],
            "metadata": {},
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['title'], "Test Task")

    def test_list_tasks(self):
        url = reverse('tasks-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)