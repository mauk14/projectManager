from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer
from rest_framework.decorators import api_view, permission_classes
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class RegisterView(APIView):
    permission_classes = [AllowAny]


    @swagger_auto_schema(
        operation_description="Register a new user",
        request_body=UserSerializer,
        responses={
            201: UserSerializer(),
            400: openapi.Response(
                description="Bad request",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'username': openapi.Schema(type=openapi.TYPE_STRING, description="Username"),
                        'password': openapi.Schema(type=openapi.TYPE_STRING, description="Password"),
                        'email': openapi.Schema(type=openapi.TYPE_STRING, description="Email"),
                    },
                ),
            ),
            409: openapi.Response(
                description="Conflict",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(type=openapi.TYPE_STRING, description="User already exists"),
                    },
                ),
            ),
        }  
    )
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Logout a user",
        manual_parameters=[
            openapi.Parameter(
                name="Authorization",
                in_=openapi.IN_HEADER,
                description="JWT token format: Bearer <token>",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'refresh': openapi.Schema(type=openapi.TYPE_STRING, description="Refresh token"),
            },
        ),
        responses={
            205: openapi.Response(description="Logout successful"),
            400: openapi.Response(description="Bad request"),
            401: openapi.Response(description="Unauthorized"),
        },
    )
    def post(self, request):
        try:
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return Response({"detail": "Invalid token format"}, status=status.HTTP_400_BAD_REQUEST)

            refresh_token = request.data["refresh"]
            if not refresh_token:
                return Response({"detail": "Refresh token required"}, status=status.HTTP_400_BAD_REQUEST)
            
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        

@swagger_auto_schema(
    method='post',
    operation_description="Authenticate a user with JwT tokens",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['username', 'password'],
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING, description="Username"),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description="Password"),
        },
    ),
    responses={
        200: openapi.Response(
            description="Successful authentication",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'refresh': openapi.Schema(type=openapi.TYPE_STRING, description="Refresh token"),
                    'access': openapi.Schema(type=openapi.TYPE_STRING, description="Access token"),
                }
            ),
        ),
        401: openapi.Response(description="Wrong credentials"),
    },
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    from django.contrib.auth import authenticate
    username = request.data.get("username")
    password = request.data.get("password")
    user = authenticate(username=username, password=password)
    if user is not None:
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
    return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)