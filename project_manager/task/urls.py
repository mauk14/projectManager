from django.urls import path
from .views import TaskView

urlpatterns = [
    path('', TaskView.as_view(), name='projects'),
    path('<int:task_id>/', TaskView.as_view(), name='project_detail'),
]
