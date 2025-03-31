from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Project, ProjectRole, ProjectUser
from .serializers import ProjectSerializer

# Create your views here.
class ProjectView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, project_id=None):
        if project_id:
            project = get_object_or_404(Project, id=project_id)
            if request.user.is_superuser or request.user in project.staff.all():
                return Response(ProjectSerializer(project).data)
            return Response({"error": "Access denied"}, status=status.HTTP_403_FORBIDDEN)
        
        if request.user.is_superuser:
            projects = Project.objects.all()
        else:
            projects = Project.objects.filter(staff=request.user)
        
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = ProjectSerializer(data=request.data)
        print(request.user)
        if serializer.is_valid():
            project = serializer.save()
            project.create_default_roles(request.user)
            return Response(ProjectSerializer(project).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)
        creator_role = ProjectRole.objects.filter(project=project, name="creator").first()
        is_creator = ProjectUser.objects.filter(project=project, user=request.user, role=creator_role).exists()
        if is_creator or request.user.is_superuser:
            serializer = ProjectSerializer(project, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": "Access denied"}, status=status.HTTP_403_FORBIDDEN)
    
    def delete(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)
        role = ProjectRole.objects.filter(project=project, name="creator").first()
        if request.user in ProjectUser.objects.filter(project=project, user=request.user, role=role).exists() or request.user.is_superuser:
            project.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"error": "Access denied"}, status=status.HTTP_403_FORBIDDEN)