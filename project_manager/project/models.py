from django.db import models
from auth_app.models import User
from django.utils.timezone import now


# class Permission(models.Model):
#     name = models.CharField(max_length=100, unique=True)

#     def __str__(self):
#         return self.name

#     @classmethod
#     def populate_default_permissions(cls):
#         default_permissions = [
#             "edit_project", "delete_project", "create_role", "create_task", "edit_task",
#             "add_user_to_lower_role", "leave_comment_on_task", "submit_for_review",
#             "confirm_completion", "send_for_revision", "cancel_task", "delete_task",
#             "start_execution", "track_time"
#         ]
#         for perm_name in default_permissions:
#             cls.objects.get_or_create(name=perm_name)


class ProjectRole(models.Model):
    name = models.CharField(max_length=50)
    project = models.ForeignKey("Project", on_delete=models.CASCADE, related_name="roles", null=True, blank=True)
    # permissions = models.ManyToManyField(Permission, blank=True)
    # priority = models.FloatField()

    def __str__(self):
        return f"{self.name} ({self.project.name if self.project else 'Global'})"


class Project(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateTimeField(default=now)
    end_date = models.DateTimeField(null=True, blank=True)
    staff = models.ManyToManyField(User, through="ProjectUser", related_name="projects", blank=True)
    
    def __str__(self):
        return self.name
    
    def create_default_roles(self, creator):
        creator_role = ProjectRole.objects.create(name="creator", project=self)
        ProjectRole.objects.create(name="manager", project=self)
        ProjectRole.objects.create(name="executor", project=self)
        
        
        ProjectUser.objects.create(user=creator, project=self, role=creator_role)
    
    # def add_custom_roles(self, roles_data, creator):
    #     creator_project_user = ProjectUser.objects.filter(user=creator, project=self).first()
    #     if not creator_project_user:
    #         raise ValueError("Access denied")

    #     max_priority = creator_project_user.role.priority

    #     for role_data in roles_data:
    #         if role_data["priority"] >= max_priority:
    #             raise ValueError("The priority of the new role cannot be higher than the priority of the requester.")
            
    #         role = ProjectRole.objects.create(
    #             name=role_data["name"],
    #             project=self,
    #             priority=role_data["priority"]
    #         )
    #         role.permissions.set(Permission.objects.filter(name__in=role_data.get("permissions", [])))


class ProjectUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    role = models.ForeignKey(ProjectRole, on_delete=models.CASCADE)