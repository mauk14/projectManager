from rest_framework.test import APITestCase
from auth_app.models import User
from .models import Project, ProjectUser
from django.urls import reverse
from rest_framework import status
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken


class ProjectViewTests(APITestCase):
    def setUp(self):
        self.creator = User.objects.create_user(username="creator", password="password", email="test1@example.com")
        self.manager = User.objects.create_user(username="manager", password="password", email="test2@example.com")
        self.executor = User.objects.create_user(username="executor", password="password", email="test3@example.com")

        self.project = Project.objects.create(name="Test Project", start_date=timezone.now())

        ProjectUser.objects.create(user=self.creator, project=self.project, role="creator")
        ProjectUser.objects.create(user=self.manager, project=self.project, role="manager")
        ProjectUser.objects.create(user=self.executor, project=self.project, role="executor")

        self.token_creator = RefreshToken.for_user(self.creator)
        self.token_manager = RefreshToken.for_user(self.manager)
        self.token_executor = RefreshToken.for_user(self.executor)

        self.auth_header_creator = {'Authorization': f'Bearer {str(self.token_creator.access_token)}'}
        self.auth_header_manager = {'Authorization': f'Bearer {str(self.token_manager.access_token)}'}
        self.auth_header_executor = {'Authorization': f'Bearer {str(self.token_executor.access_token)}'}

    def test_get_project_details(self):
        url = reverse('project_detail', kwargs={'project_id': self.project.id})
        
        response = self.client.get(url, HTTP_AUTHORIZATION=self.auth_header_creator['Authorization'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        response = self.client.get(url, HTTP_AUTHORIZATION=self.auth_header_manager['Authorization'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        response = self.client.get(url, HTTP_AUTHORIZATION=self.auth_header_executor['Authorization'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_project_list(self):
        url = reverse('projects')
        
        response = self.client.get(url, HTTP_AUTHORIZATION=self.auth_header_creator['Authorization'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        response = self.client.get(url, HTTP_AUTHORIZATION=self.auth_header_manager['Authorization'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        response = self.client.get(url, HTTP_AUTHORIZATION=self.auth_header_executor['Authorization'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_project(self):
        url = reverse('projects')
        data = {
            "name": "New Project",
            "description": "Project description",
            "start_date": timezone.now().isoformat(),
            "end_date": (timezone.now() + timezone.timedelta(days=30)).isoformat()
        }
        
        response = self.client.post(url, data, HTTP_AUTHORIZATION=self.auth_header_creator['Authorization'])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        project = Project.objects.get(name="New Project")
        self.assertEqual(project.description, "Project description")

    def test_update_project(self):
        url = f"/api/projects/{self.project.id}/"
        data = {
            "name": "Updated Project",
            "description": "Updated description",
            "start_date": timezone.now().isoformat(),
            "end_date": (timezone.now() + timezone.timedelta(days=60)).isoformat()
        }
        
        response = self.client.patch(url, data, HTTP_AUTHORIZATION=self.auth_header_creator['Authorization'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        

    def test_delete_project(self):
        url = f"/api/projects/{self.project.id}/"
        
        response = self.client.delete(url, HTTP_AUTHORIZATION=self.auth_header_creator['Authorization'])
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        

# class ProjectStaffPatchTests(APITestCase):
#     def setUp(self):
#         self.creator = User.objects.create_user(username="creator", password="pass123")
#         self.manager = User.objects.create_user(username="manager", password="pass123")
#         self.executor = User.objects.create_user(username="executor", password="pass123")
#         self.new_user = User.objects.create_user(username="new_user", password="pass123")

#         self.project = Project.objects.create(name="Test Project")

#         self.creator_role = ProjectRole.objects.create(name="creator", project=self.project)
#         self.manager_role = ProjectRole.objects.create(name="manager", project=self.project)
#         self.executor_role = ProjectRole.objects.create(name="executor", project=self.project)

#         ProjectUser.objects.create(user=self.creator, project=self.project, role=self.creator_role)

#         self.client.force_authenticate(user=self.creator)
        
#         self.url = f"/api/projects/{self.project.id}/"