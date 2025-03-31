from django.db import models

# Create your models here.

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