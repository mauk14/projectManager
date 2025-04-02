from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Project, ProjectUser
from auth_app.models import User
from .serializers import ProjectSerializer
from django.utils.timezone import now


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

        if serializer.is_valid():
            project = serializer.save()
            project.create_default_roles(request.user)
            return Response(ProjectSerializer(project).data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)

        if not (project.has_creator_access(request.user) or request.user.is_superuser):
            return Response({"error": "Access denied"}, status=status.HTTP_403_FORBIDDEN)
        
        allowed_roles = {"manager", "executor"}
        staff_data = request.data.get("staff", [])
        if staff_data:
            for user_data in staff_data:
                user_id = user_data.get("user_id")
                role = user_data.get("role", "executor")

                if not user_id:
                    return Response({"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST)
                
                if role not in allowed_roles:
                    return Response({"error": f"Invalid role '{role}'"}, status=status.HTTP_400_BAD_REQUEST)

                user = get_object_or_404(User, id=user_id)

                ProjectUser.objects.get_or_create(user=user, project=project, role=role)


        serializer = ProjectSerializer(project, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    
    def delete(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)

        if project.has_creator_access(request.user) or request.user.is_superuser:
            project.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        return Response({"error": "Access denied"}, status=status.HTTP_403_FORBIDDEN)
    
class ProjectTimeTrackingAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)
        user = request.user

        if user not in project.staff.all() and not user.is_superuser:
            return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)

        return Response(self.get_project_time_info(project), status=status.HTTP_200_OK)
    
    def get_project_time_info(self, project):
        return {
            'name': project.name,
            'start_date': project.start_date,
            'end_date': project.end_date,
            'time_since_start': (now() - project.start_date).total_seconds(),
            'time_since_end': (now() - project.end_date).total_seconds() if project.end_date else None,
            'time_remaining': (project.end_date - now()).total_seconds() if project.end_date else None,
        }