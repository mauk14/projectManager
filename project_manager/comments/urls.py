from django.urls import path
from .views import CommentAPIView

urlpatterns = [
    path('', CommentAPIView.as_view(), name='comments'),
    path('<int:comment_id>/', CommentAPIView.as_view(), name='comment_detail'),
]