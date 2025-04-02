from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.utils.timezone import now
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Task
from auth_app.models import User
from project.models import Project

class TaskViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user1', password='password', email='test@example.com')
        self.project = Project.objects.create(name='Test Project')
        self.project.create_default_roles(self.user)
        self.task = Task.objects.create(title='Test Task', project=self.project)
        self.task.assigned_to.add(self.user)

        self.token_user = RefreshToken.for_user(self.user)
        self.auth_header_user = {'Authorization': f'Bearer {str(self.token_user.access_token)}'}

        self.task_url = reverse('task_detail', kwargs={'task_id': self.task.id})
        self.task_list_url = reverse('tasks')

    def test_create_task(self):
        data = {"title": "New Task", "project": self.project.id, "description": "test",}
        response = self.client.post(self.task_list_url, data, HTTP_AUTHORIZATION=self.auth_header_user['Authorization'])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_task(self):
        response = self.client.get(self.task_url, HTTP_AUTHORIZATION=self.auth_header_user['Authorization'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Task')

    def test_update_task(self):
        data = {"title": "Updated Task"}
        response = self.client.patch(self.task_url, data,  HTTP_AUTHORIZATION=self.auth_header_user['Authorization'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, "Updated Task")

    def test_delete_task(self):
        response = self.client.delete(self.task_url, HTTP_AUTHORIZATION=self.auth_header_user['Authorization'])
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Task.objects.filter(id=self.task.id).exists())

    def test_access_denied_for_unauthorized_user(self):
        self.auth_header_user = {'Authorization': f'Bearer '}
        response = self.client.get(self.task_url, HTTP_AUTHORIZATION=self.auth_header_user['Authorization'])
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)            