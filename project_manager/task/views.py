from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Task
from .serializers import TaskSerializer
from project.models import Project, ProjectRole, ProjectUser
from django.shortcuts import get_object_or_404

# Create your views here.
class TaskView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Handle POST request to create a new task
        project = get_object_or_404(Project, id=request.data.get("project"))
        if ProjectUser.objects.filter(user=request.user, project=project, role__name__in=["creator", "manager"]).exists() or request.user.is_superuser:
            serializer = TaskSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  
        return Response({"error": "Access denied"}, status=status.HTTP_403_FORBIDDEN)

    def get(self, request, task_id=None):
        if task_id:
            task = get_object_or_404(Task, id=task_id)
            if request.user.is_superuser or request.user in task.project.staff.all():
                return Response(TaskSerializer(task).data)
            return Response({"error": "Access denied"}, status=status.HTTP_403_FORBIDDEN)
        
        if request.user.is_superuser:
            tasks = Task.objects.all()
        tasks = Task.objects.filter(project__staff=request.user)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)    
    
    def delete(self, request, task_id):
        task = get_object_or_404(Task, id=task_id)
        if ProjectUser.objects.filter(user=request.user, project=task.project, role__name__in=["creator", "manager"]).exists() or request.user.is_superuser:
            task.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        return Response({"error": "Access denied"}, status=status.HTTP_403_FORBIDDEN)
    
    def patch(self, request, task_id):
        task = get_object_or_404(Task, id=task_id)

        if ProjectUser.objects.filter(user=request.user, project=task.project, role__name__in=["creator", "manager"]).exists() or request.user.is_superuser:
            serializer = TaskSerializer(task, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({"error": "Access denied"}, status=status.HTTP_403_FORBIDDEN)