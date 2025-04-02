from django.test import TestCase
from rest_framework.test import APITestCase
from auth_app.models import User
from .models import Project, ProjectRole, ProjectUser
from django.urls import reverse
from rest_framework import status
from django.utils import timezone


class ProjectViewTests(APITestCase):
    def setUp(self):
        self.creator = User.objects.create_user(username="creator", password="password")
        self.manager = User.objects.create_user(username="manager", password="password")
        self.executor = User.objects.create_user(username="executor", password="password")

        self.project = Project.objects.create(name="Test Project", start_date=timezone.now())

        ProjectUser.objects.create(user=self.creator, project=self.project, role="creator")
        ProjectUser.objects.create(user=self.manager, project=self.project, role="manager")
        ProjectUser.objects.create(user=self.executor, project=self.project, role="executor")

        self.client.login(username='creator', password='password')

    def test_get_project_details(self):
        url = reverse('project_detail', kwargs={'project_id': self.project.id})
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.client.login(username='manager', password='password')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        
        self.client.login(username='executor', password='password')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)    

class ProjectStaffPatchTests(APITestCase):
    def setUp(self):
        self.creator = User.objects.create_user(username="creator", password="pass123")
        self.manager = User.objects.create_user(username="manager", password="pass123")
        self.executor = User.objects.create_user(username="executor", password="pass123")
        self.new_user = User.objects.create_user(username="new_user", password="pass123")

        self.project = Project.objects.create(name="Test Project")

        self.creator_role = ProjectRole.objects.create(name="creator", project=self.project)
        self.manager_role = ProjectRole.objects.create(name="manager", project=self.project)
        self.executor_role = ProjectRole.objects.create(name="executor", project=self.project)

        ProjectUser.objects.create(user=self.creator, project=self.project, role=self.creator_role)

        self.client.force_authenticate(user=self.creator)
        
        self.url = f"/api/projects/{self.project.id}/"