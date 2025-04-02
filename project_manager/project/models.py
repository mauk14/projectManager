from django.db import models
from auth_app.models import User
from django.utils.timezone import now

class Project(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateTimeField(default=now)
    end_date = models.DateTimeField(null=True, blank=True)
    staff = models.ManyToManyField(User, through="ProjectUser", related_name="projects", blank=True)
    
    def __str__(self):
        return self.name
    
    def create_default_roles(self, creator):
        ProjectUser.objects.create(user=creator, project=self, role="creator")

    def has_creator_access(self, user):
        return self.projectuser_set.filter(user=user, role__name="creator").exists()   

    def has_manager_access(self, user):
        return self.projectuser_set.filter(user=user, role__name="manager").exists()
 

class ProjectUser(models.Model):
    ROLE_CHOICES = [
        ('creator', 'Creator'),
        ('manager', 'Manager'),
        ('executor', 'Executor'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)