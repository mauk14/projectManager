from django.urls import path
from .views import ProjectView, ProjectTimeTrackingAPIView

urlpatterns = [
    path('', ProjectView.as_view(), name='projects'),
    path('<int:project_id>/', ProjectView.as_view(), name='project_detail'),
    path('time/<int:project_id>/', ProjectTimeTrackingAPIView.as_view(), name='project_detail'),
]
