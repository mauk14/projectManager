from django.db import models
from project.models import ProjectUser


class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    due_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=50, choices=[
        ('new', 'New'),
        ('in_progress', 'In Progress'), 
        ('on_checking', 'On Checking'),
        ('completed', 'Completed'), 
        ('canceled', 'Canceled')], default='new')
    project = models.ForeignKey('project.Project', on_delete=models.CASCADE, related_name='tasks')
    assigned_to = models.ManyToManyField('auth_app.User', related_name='tasks', blank=True)

    def __str__(self):
        return self.title
    
    def has_creator_access(self, user):
        return self.project.projectuser_set.filter(user=user, project=self.project, role__name="creator").exists()

    def has_manager_access(self, user):
        return self.project.projectuser_set.filter(user=user, project=self.project, role__name="manager").exists()

    def has_executor_access(self, user):
        return self.assigned_to.filter(id=user.id).exists()
    
    def user_has_access(self, user):
       
        if self.has_creator_access(user):
            return True  
        if self.has_manager_access(user):
            return True  
        if self.has_executor_access(user):
            return True  
        return False