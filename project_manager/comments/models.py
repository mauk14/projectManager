from django.db import models


class Comment(models.Model):
    task = models.ForeignKey("task.Task", on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey('auth_app.User', on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.task.title}"
    
    def user_has_access(self, user):
        return (
            user.is_superuser
            or self.task.project.projectuser_set.filter(user=user, role__in=["creator", "manager"]).exists()
            or self.task.assigned_to.filter(id=user.id).exists()
        )