from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Comment
from .serializers import CommentSerializer
from django.shortcuts import get_object_or_404
from task.models import Task


class CommentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, task_id,comment_id=None):
        
        task = get_object_or_404(Task, id=task_id)

        if not task.user_has_access(request.user):
            return Response({"error": "Access denied"}, status=status.HTTP_403_FORBIDDEN)
        
        if comment_id:
            comment = get_object_or_404(Comment, id=comment_id)
            serializer = CommentSerializer(comment)
            return Response(serializer.data)
        
        comments = Comment.objects.filter(task_id=task_id)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, task_id):
        task = get_object_or_404(Task, id=task_id)
        user = request.user
        
        if not Comment(task=task).user_has_access(user):
            return Response({"error": "Access denied"}, status=status.HTTP_403_FORBIDDEN)
        
        data = request.data.copy()
        data["task"] = task_id
        data["user"] = request.user.id
        serializer = CommentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, task_id, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        user = request.user

        if not comment.user_has_access(user) and comment.user != user:
            return Response({"error": "Access denied"}, status=status.HTTP_403_FORBIDDEN)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)