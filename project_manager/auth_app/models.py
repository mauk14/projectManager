from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager



class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None):
        if not email:
            raise ValueError("Email is required")
        user = self.model(username=username, email=self.normalize_email(email))
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, email, password):
        user = self.create_user(username, email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user
    

class User(AbstractUser):
    email = models.EmailField(unique=True)
    objects = UserManager()

    groups = models.ManyToManyField(
        "auth.Group", related_name="custom_user_groups"
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission", related_name="custom_user_permissions"
    )
    
    def __str__(self):
        return self.username
