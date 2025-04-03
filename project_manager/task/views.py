from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Task
from .serializers import TaskSerializer
from project.models import Project, ProjectUser
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class TaskView(APIView):
    permission_classes = [IsAuthenticated]


    @swagger_auto_schema(
        operation_description="Create a new task",
        manual_parameters=[
            openapi.Parameter(
                name="Authorization",
                in_=openapi.IN_HEADER,
                description="JWT token format: Bearer <token>",
                type=openapi.TYPE_STRING,
                required=True
            ),
        ],
        request_body=TaskSerializer,
        responses={
            201: TaskSerializer(),
            400: openapi.Response(
                description="Bad request",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(type=openapi.TYPE_STRING, description="Invalid data"),
                    },
                ),
            ),
            403: openapi.Response(
                description="Access denied",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description="Access denied"),
                    },
                ),
            ),
        }
    )
    def post(self, request):
        # Handle POST request to create a new task
        project = get_object_or_404(Project, id=request.data.get("project"))
        if project.has_creator_access(request.user) or project.has_manager_access(request.user) or request.user.is_superuser:
            serializer = TaskSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  
        return Response({"error": "Access denied"}, status=status.HTTP_403_FORBIDDEN)

    @swagger_auto_schema(
        operation_description="Get task details or list of tasks",
        manual_parameters=[
            openapi.Parameter(
                name="Authorization",
                in_=openapi.IN_HEADER,
                description="JWT token format: Bearer <token>",
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                name="task_id",
                in_=openapi.IN_PATH,
                description="Task ID",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ],
        responses={
            200: TaskSerializer(many=True),
            403: openapi.Response(
                description="Access denied",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description="Access denied"),
                    },
                ),
            ),
        }
    )
    def get(self, request, task_id=None):
        if task_id:
            task = get_object_or_404(Task, id=task_id)
            if task.user_has_access(request.user) or request.user.is_superuser:
                return Response(TaskSerializer(task).data)
            return Response({"error": "Access denied"}, status=status.HTTP_403_FORBIDDEN)
        
        if request.user.is_superuser:
            tasks = Task.objects.all()
            serializer = TaskSerializer(tasks, many=True)
            return Response(serializer.data)   
         
        tasks = Task.objects.filter(project__staff=request.user)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)    
    
    @swagger_auto_schema(
        operation_description="Delete a task",
        manual_parameters=[
            openapi.Parameter(
                name="Authorization",
                in_=openapi.IN_HEADER,
                description="JWT token format: Bearer <token>",
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                name="task_id",
                in_=openapi.IN_PATH,
                description="Task ID",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ],
        responses={
            204: openapi.Response(description="No content"),
            403: openapi.Response(
                description="Access denied",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description="Access denied"),
                    },
                ),
            ),
        }
    )
    def delete(self, request, task_id):
        task = get_object_or_404(Task, id=task_id)

        if task.has_creator_access(request.user) or task.has_manager_access(request.user) or request.user.is_superuser:
            task.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        return Response({"error": "Access denied"}, status=status.HTTP_403_FORBIDDEN)
    
    @swagger_auto_schema(
        operation_description="Update a task",
        manual_parameters=[
            openapi.Parameter(
                name="Authorization",
                in_=openapi.IN_HEADER,
                description="JWT token format: Bearer <token>",
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                name="task_id",
                in_=openapi.IN_PATH,
                description="Task ID",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ],
        request_body=TaskSerializer,
        responses={
            200: TaskSerializer(),
            400: openapi.Response(
                description="Bad request",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(type=openapi.TYPE_STRING, description="Invalid data"),
                    },
                ),
            ),
            403: openapi.Response(
                description="Access denied",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description="Access denied"),
                    },
                ),
            ),
        }
    )
    def patch(self, request, task_id):
        task = get_object_or_404(Task, id=task_id)

        if task.has_creator_access(request.user) or task.has_manager_access(request.user) or request.user.is_superuser:
            serializer = TaskSerializer(task, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({"error": "Access denied"}, status=status.HTTP_403_FORBIDDEN)


class TaskTimeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, task_id):
        task = get_object_or_404(Task, id=task_id)

        if not (task.user_has_access(request.user) or request.user.is_superuser):
            return Response({"error": "Access denied"}, status=status.HTTP_403_FORBIDDEN)
        return Response(self.get_task_time_info(task))
            
    def get_task_time_info(self, task):
        return {
            'created_at': task.created_at,
            'updated_at': task.updated_at,
            'due_date': task.due_date,
            'time_since_creation': (now() - task.created_at).total_seconds(),
            'time_since_update': (now() - task.updated_at).total_seconds(),
            'time_remaining': (task.due_date - now()).total_seconds() if task.due_date else None,
        }        