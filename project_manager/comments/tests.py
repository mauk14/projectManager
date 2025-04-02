from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Comment
from project.models import Project
from task.models import Task
from auth_app.models import User
from django.utils.timezone import now
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken

class CommentAPIViewTests(APITestCase): 
    def setUp(self):
        self.user = User.objects.create_user(username='user1', password='password', email="test@example.com")
        self.project = Project.objects.create(name='Test Project')
        self.project.create_default_roles(self.user)
        self.task = Task.objects.create(title='Test Task', project=self.project, created_at=now(), updated_at=now())
        self.comment = Comment.objects.create(task=self.task, user=self.user, text='Test comment')

        self.token_user = RefreshToken.for_user(self.user)
        self.auth_header_user = {'Authorization': f'Bearer {str(self.token_user.access_token)}'}

        self.comment_list_url = reverse('comments', kwargs={'task_id': self.task.id})
        self.comment_detail_url = reverse('comment_detail', kwargs={'task_id': self.task.id, 'comment_id': self.comment.id})

    def test_get_comments(self):
        response = self.client.get(self.comment_list_url, HTTP_AUTHORIZATION=self.auth_header_user['Authorization'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_comment_by_id(self):
        response = self.client.get(self.comment_detail_url, HTTP_AUTHORIZATION=self.auth_header_user['Authorization'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['text'], 'Test comment')

    def test_create_comment(self):
        data = {"text": "New Comment"}
        response = self.client.post(self.comment_list_url, data, HTTP_AUTHORIZATION=self.auth_header_user['Authorization'])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 2)

    def test_delete_comment(self):
        response = self.client.delete(self.comment_detail_url,  HTTP_AUTHORIZATION=self.auth_header_user['Authorization'])
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Comment.objects.filter(id=self.comment.id).exists())

    def test_access_denied_for_unauthorized_user(self):
        self.auth_header_user = {'Authorization': f'Bearer '}
        response = self.client.get(self.comment_list_url, HTTP_AUTHORIZATION=self.auth_header_user['Authorization'])
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)    