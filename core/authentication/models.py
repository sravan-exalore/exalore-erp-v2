from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    is_core_admin = models.BooleanField(default=False)

    class Meta:
        db_table = "core_users"
