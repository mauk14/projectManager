from django.urls import path
from .views import ProjectView

urlpatterns = [
    path('', ProjectView.as_view(), name='projects'),
    path('<int:project_id>/', ProjectView.as_view(), name='project_detail'),
]
