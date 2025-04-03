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
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class ProjectView(APIView):
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Get project details",
        manual_parameters=[
            openapi.Parameter(
                name="project_id",
                in_=openapi.IN_PATH,
                description="Project ID",
                type=openapi.TYPE_INTEGER,
            ),
        ],
        responses={
            200: ProjectSerializer(),
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
    

    @swagger_auto_schema(
        operation_description="Create a new project",
        manual_parameters=[
            openapi.Parameter(
                name="Authorization",
                in_=openapi.IN_HEADER,
                description="JWT token format: Bearer <token>",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        request_body=ProjectSerializer,
        responses={
            201: ProjectSerializer(),
            400: openapi.Response(
                description="Bad request",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description="Invalid data"),
                    },
                ),
            ),
        }
    )
    def post(self, request):
        serializer = ProjectSerializer(data=request.data)

        if serializer.is_valid():
            project = serializer.save()
            project.create_default_roles(request.user)
            return Response(ProjectSerializer(project).data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        operation_description="Update project details",
        manual_parameters=[
            openapi.Parameter(
                name="project_id",
                in_=openapi.IN_PATH,
                description="Project ID",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                name="Authorization",
                in_=openapi.IN_HEADER,
                description="JWT token format: Bearer <token>",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        request_body=ProjectSerializer,
        responses={
            200: ProjectSerializer(),
            400: openapi.Response(
                description="Bad request",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description="Invalid data"),
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
        
    @swagger_auto_schema(
        operation_description="Delete a project",
        manual_parameters=[
            openapi.Parameter(
                name="project_id",
                in_=openapi.IN_PATH,
                description="Project ID",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                name="Authorization",
                in_=openapi.IN_HEADER,
                description="JWT token format: Bearer <token>",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            204: openapi.Response(description="Project deleted"),
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
    def delete(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)

        if project.has_creator_access(request.user) or request.user.is_superuser:
            project.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        return Response({"error": "Access denied"}, status=status.HTTP_403_FORBIDDEN)
    
class ProjectTimeTrackingAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get project time tracking information",
        manual_parameters=[
            openapi.Parameter(
                name="project_id",
                in_=openapi.IN_PATH,
                description="Project ID",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                name="Authorization",
                in_=openapi.IN_HEADER,
                description="JWT token format: Bearer <token>",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="Project time tracking information",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'name': openapi.Schema(type=openapi.TYPE_STRING, description="Project name"),
                        'start_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description="Project start date"),
                        'end_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description="Project end date"),
                        'time_since_start': openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT, description="Time since project started in seconds"),
                        'time_since_end': openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT, description="Time since project ended in seconds"),
                        'time_remaining': openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT, description="Time remaining until project ends in seconds"),
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