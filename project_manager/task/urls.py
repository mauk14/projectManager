from django.urls import path, include
from .views import TaskView, TaskTimeAPIView

urlpatterns = [
    path('', TaskView.as_view(), name='tasks'),
    path('<int:task_id>/', TaskView.as_view(), name='task_detail'),
    path('time/<int:task_id>/', TaskTimeAPIView.as_view(), name='task_time'),
    path('<int:task_id>/comments/', include('comments.urls'), name='comment_task'),
]
