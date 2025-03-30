from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


class Role(models.TextChoices):
    ADMIN = "admin", "Admin"
    MANAGER = "manager", "Manager"
    EXECUTOR = "executor", "Executor"


class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, role=Role.EXECUTOR):
        if not email:
            raise ValueError("Email is required")
        user = self.model(username=username, email=self.normalize_email(email), role=role)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, email, password):
        user = self.create_user(username, email, password, role=Role.ADMIN)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user
    

class User(AbstractUser):
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.EXECUTOR)
    objects = UserManager()

    groups = models.ManyToManyField(
        "auth.Group", related_name="custom_user_groups"
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission", related_name="custom_user_permissions"
    )
    
    def __str__(self):
        return self.username
